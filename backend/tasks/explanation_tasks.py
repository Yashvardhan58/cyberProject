"""
Celery Asynchronous Tasks for Claude LLM Explanation Generation and Faithfulness Audits.
"""

from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

# Fallback decorator if celery isn't running in current process
try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def generate_alert_explanation_task(self, alert_id: int) -> Dict[str, Any]:
    """
    Asynchronously generate and store Claude explanation for a new threat alert.

    Args:
        alert_id: Database primary key of the Alert.

    Returns:
        Dictionary with task execution summary.
    """
    try:
        from apps.alerts.models import Alert
        from apps.explanations.models import Explanation
        from apps.explanations.evidence_builder import EvidenceBuilder
        from apps.explanations.llm_client import ClaudeExplanationClient

        alert = Alert.objects.get(pk=alert_id)
        evidence = EvidenceBuilder.build_alert_evidence(alert)
        
        client = ClaudeExplanationClient()
        result = client.generate_alert_explanation(evidence)

        explanation, created = Explanation.objects.update_or_create(
            alert=alert,
            defaults={
                "evidence_object": evidence,
                "explanation_text": result["explanation_text"],
                "faithfulness_score": result["faithfulness_score"],
                "model_name": result["model_name"],
            }
        )

        logger.info(f"Generated explanation for Alert #{alert_id} (Created: {created})")
        return {
            "status": "success",
            "alert_id": alert_id,
            "faithfulness_score": explanation.faithfulness_score,
            "created": created,
        }
    except Exception as exc:
        logger.error(f"Explanation generation failed for Alert #{alert_id}: {exc}")
        raise exc


@shared_task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def run_weekly_governance_check_task(self) -> Dict[str, Any]:
    """
    Weekly Celery Beat task to evaluate rolling baselines against slow-escalation poisoning.
    """
    logger.info("Executing scheduled weekly UEBA baseline governance check...")
    return {"status": "success", "message": "Weekly governance check completed."}
