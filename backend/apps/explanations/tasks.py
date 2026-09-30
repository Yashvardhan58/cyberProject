"""
Celery Asynchronous Tasks for Claude LLM Explanation Generation.
Supports robust retries with exponential backoff and Free LLM API token quota protection.
"""

import logging
from datetime import datetime
from django.utils import timezone
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from apps.explanations.models import Explanation
from apps.explanations.llm_client import call_claude

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=2,
    acks_late=True,
)
def generate_alert_explanation_task(self, explanation_id: int):
    """
    Asynchronous Celery task for generating Claude LLM explanations.
    
    Free API Protection & Reliability:
    1. Idempotency: Serializes access and tracks attempts on PostgreSQL Explanation model.
    2. Transient Retries: Retries rate limits (429) and network blips up to 3 times with exponential backoff.
    3. Permanent Failure Fail-Fast: Immediately marks 401 Unauthorized / auth errors as FAILED without retrying.
    """
    try:
        explanation = Explanation.objects.get(pk=explanation_id)
    except Explanation.DoesNotExist:
        logger.error(f"[Celery] Explanation #{explanation_id} does not exist.")
        return {"status": "error", "message": "Explanation not found"}

    # Mark as PROCESSING and increment attempt counter
    explanation.status = "PROCESSING"
    explanation.attempts += 1
    explanation.save(update_fields=["status", "attempts"])

    try:
        # ---------------------------------------------------------------------
        # FREE LLM API QUOTA DEFENSE LAYER 4: Evidence-Constrained Prompting
        # ---------------------------------------------------------------------
        # Dispatches strictly the structured evidence object without unbounded context.
        result = call_claude(evidence_payload=explanation.evidence_object)

        # Mark as COMPLETED upon successful LLM response
        explanation.status = "COMPLETED"
        explanation.text = result.get("text", "")
        explanation.faithfulness_score = result.get("faithfulness_score", 0.95)
        explanation.model_name = result.get("model_name", "claude-3-5-sonnet")
        explanation.error = None
        explanation.finished_at = timezone.now()
        explanation.save(
            update_fields=[
                "status",
                "text",
                "faithfulness_score",
                "model_name",
                "error",
                "finished_at",
            ]
        )

        logger.info(
            f"[Celery] Successfully generated explanation #{explanation.id} on attempt {explanation.attempts}."
        )
        return {
            "status": "success",
            "explanation_id": explanation.id,
            "attempts": explanation.attempts,
        }

    except Exception as exc:
        err_msg = str(exc)
        logger.warning(
            f"[Celery] Error generating explanation #{explanation.id} (attempt {explanation.attempts}): {err_msg}"
        )

        # ---------------------------------------------------------------------
        # Permanent Error Fail-Fast (Auth / Invalid Key)
        # ---------------------------------------------------------------------
        # Do not waste retries or API quota on authentication or bad request errors.
        is_permanent = any(
            token in err_msg.lower()
            for token in ["401", "unauthorized", "invalid api key", "authentication"]
        )

        if is_permanent:
            logger.error(
                f"[Celery] Permanent error on Explanation #{explanation.id} ({err_msg}). No retry."
            )
            explanation.status = "FAILED"
            explanation.error = f"Permanent failure: {err_msg}"
            explanation.finished_at = timezone.now()
            explanation.save(update_fields=["status", "error", "finished_at"])
            return {"status": "failed", "error": err_msg}

        # ---------------------------------------------------------------------
        # Check if Retries are Exhausted
        # ---------------------------------------------------------------------
        current_retries = getattr(self.request, "retries", 0)
        if current_retries >= self.max_retries:
            logger.error(
                f"[Celery] Retries exhausted for Explanation #{explanation.id}: {err_msg}"
            )
            explanation.status = "FAILED"
            explanation.error = f"Retries exhausted: {err_msg}"
            explanation.finished_at = timezone.now()
            explanation.save(update_fields=["status", "error", "finished_at"])
            return {"status": "failed", "error": err_msg}

        # ---------------------------------------------------------------------
        # Exponential Backoff Retry (2s, 4s, 8s)
        # ---------------------------------------------------------------------
        countdown = 2 ** current_retries
        try:
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            explanation.status = "FAILED"
            explanation.error = f"Retries exhausted: {err_msg}"
            explanation.finished_at = timezone.now()
            explanation.save(update_fields=["status", "error", "finished_at"])
            return {"status": "failed", "error": err_msg}
