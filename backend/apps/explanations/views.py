"""
API Views for Explanations and Interactive Analyst Chatbot.
Supports Celery 5.3 + Redis 7 Asynchronous Non-Blocking Explanation Generation.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from datetime import timedelta
from django.utils import timezone
from celery import current_app
from celery.exceptions import OperationalError as CeleryOperationalError
from kombu.exceptions import OperationalError as KombuOperationalError

from .models import Explanation, ChatSession, ChatMessage
from .serializers import ExplanationSerializer, ChatSessionSerializer, ChatMessageSerializer
from .evidence_builder import EvidenceBuilder
from .tasks import generate_alert_explanation_task
from apps.alerts.models import Alert


class ExplanationListCreateAPIView(APIView):
    """
    POST /api/v1/explanations/
    POST /api/v1/explanations/alerts/{alert_id}/explanation/
    Initiate or retrieve asynchronous LLM explanation for an alert.
    """
    def post(self, request, alert_id: int = None):
        target_alert_id = alert_id or request.data.get("alert_id")
        if not target_alert_id:
            return Response(
                {"status": "error", "error": "alert_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alert = get_object_or_404(Alert, pk=target_alert_id)
        evidence = EvidenceBuilder.build_alert_evidence(alert)

        # ---------------------------------------------------------------------
        # FREE LLM API QUOTA DEFENSE LAYER 1: SHA-256 Evidence Hashing
        # ---------------------------------------------------------------------
        # Computes a deterministic SHA-256 fingerprint over canonical JSON.
        # If the underlying alert features have not changed, this hash remains
        # identical, guaranteeing zero duplicate token consumption on Claude API.
        evidence_hash = Explanation.compute_evidence_hash(evidence)

        # 1. Database-Level Lock & Deduplication Barrier
        with transaction.atomic():
            # select_for_update() ensures concurrent requests serialize at DB level
            explanation, created = Explanation.objects.select_for_update().get_or_create(
                alert=alert,
                evidence_hash=evidence_hash,
                defaults={
                    "evidence_object": evidence,
                    "status": "PENDING",
                    "attempts": 0,
                },
            )

            # -----------------------------------------------------------------
            # FREE LLM API QUOTA DEFENSE LAYER 2: Cache Hit Short-Circuit
            # -----------------------------------------------------------------
            # If this alert was already explained with identical telemetry, return
            # the cached PostgreSQL record immediately. Cost = 0 Claude tokens.
            if explanation.status == "COMPLETED" and not created:
                serializer = ExplanationSerializer(explanation)
                return Response(
                    {"status": "completed", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )

            # -----------------------------------------------------------------
            # STUCK-ROW RECOVERY (Audit Staleness Rule):
            # -----------------------------------------------------------------
            # If a worker died or was rebooted while status was PENDING/PROCESSING,
            # and > 10 minutes have elapsed, mark it as stale so it can re-enqueue.
            is_stale = False
            if explanation.status in ["PENDING", "PROCESSING"] and not created:
                if explanation.created_at < timezone.now() - timedelta(minutes=10):
                    is_stale = True

            # -----------------------------------------------------------------
            # FREE LLM API QUOTA DEFENSE LAYER 3: Rapid Double-Click Debounce
            # -----------------------------------------------------------------
            # If an analyst clicks "Explain" multiple times while generation is
            # in-flight, return HTTP 202 with existing job ID without enqueuing again.
            if explanation.status in ["PENDING", "PROCESSING"] and not created and not is_stale:
                return Response(
                    {
                        "status": explanation.status.lower(),
                        "id": explanation.id,
                        "alert_id": alert.id,
                        "message": f"Explanation is already {explanation.status.lower()}.",
                    },
                    status=status.HTTP_202_ACCEPTED,
                )

            # If newly created, previous attempt FAILED, or stuck/stale: prepare for queue
            should_enqueue = False
            if created or explanation.status == "FAILED" or is_stale:
                explanation.status = "PENDING"
                explanation.error = None
                explanation.evidence_object = evidence
                explanation.save(update_fields=["status", "error", "evidence_object"])
                should_enqueue = True

        # Enqueue Celery task with transaction.on_commit
        if should_enqueue:
            # -----------------------------------------------------------------
            # BROKER FAIL-FAST CHECK (Resolves Major Finding 1):
            # -----------------------------------------------------------------
            # Verify Redis broker connection before returning 202.
            # If Redis is down, fails fast with 503 instead of false-promising 202.
            # (Skipped in eager test mode so unit tests run in-memory).
            if not current_app.conf.task_always_eager:
                try:
                    with current_app.connection_for_write() as conn:
                        conn.connect()
                except Exception as broker_err:
                    explanation.status = "FAILED"
                    explanation.error = f"Message broker (Redis) unreachable: {str(broker_err)}"
                    explanation.save(update_fields=["status", "error"])
                    return Response(
                        {
                            "status": "error",
                            "error": "Task queue unavailable. Redis broker connection failed.",
                            "id": explanation.id,
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )

            # Safely dispatch Celery task only after DB transaction commits
            exp_id = explanation.id
            transaction.on_commit(lambda: generate_alert_explanation_task.delay(exp_id))

        return Response(
            {
                "status": "pending",
                "id": explanation.id,
                "alert_id": alert.id,
                "message": "Explanation queued for background generation.",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def get(self, request, alert_id: int = None):
        """
        GET /api/v1/explanations/alerts/{alert_id}/explanation/
        Returns the latest explanation for an alert.
        """
        if alert_id:
            alert = get_object_or_404(Alert, pk=alert_id)
            explanation = alert.explanations.order_by("-created_at").first()
            if not explanation:
                # Trigger queue if no explanation exists
                return self.post(request, alert_id=alert_id)
            serializer = ExplanationSerializer(explanation)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"status": "error", "error": "alert_id required"}, status=status.HTTP_400_BAD_REQUEST)


class ExplanationDetailAPIView(APIView):
    """
    GET /api/v1/explanations/{id}/
    Poll task execution status and retrieve generated explanation.
    """
    def get(self, request, id: int):
        explanation = get_object_or_404(Explanation, pk=id)
        serializer = ExplanationSerializer(explanation)
        return Response(
            {
                "status": explanation.status.lower(),
                "id": explanation.id,
                "alert_id": explanation.alert_id,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AlertChatInitAPIView(APIView):
    """
    POST /api/v1/explanations/alerts/{id}/chat/init/
    Initialize a persistent chat session between analyst and Claude SOC copilot.
    """
    def post(self, request, alert_id: int):
        alert = get_object_or_404(Alert, pk=alert_id)
        analyst = request.data.get("analyst_name", "Security Analyst")
        session_token = f"session-{alert.id}-{int(request.data.get('timestamp', 0)) or 1001}"

        session, created = ChatSession.objects.get_or_create(
            alert=alert,
            session_token=session_token,
            defaults={"analyst_name": analyst},
        )

        serializer = ChatSessionSerializer(session)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )


class ChatSessionDetailAPIView(APIView):
    """
    GET /api/v1/explanations/sessions/{session_token}/
    POST /api/v1/explanations/sessions/{session_token}/
    Send messages and retrieve conversational history.
    """
    def get(self, request, session_token: str):
        session = get_object_or_404(ChatSession, session_token=session_token)
        serializer = ChatSessionSerializer(session)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, session_token: str):
        session = get_object_or_404(ChatSession, session_token=session_token)
        user_text = request.data.get("message", "").strip()

        if not user_text:
            return Response(
                {"status": "error", "error": "Message content cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ChatMessage.objects.create(session=session, role="user", content=user_text)

        evidence = EvidenceBuilder.build_alert_evidence(session.alert)
        history = list(session.messages.values("role", "content"))

        from .llm_client import ClaudeExplanationClient
        client = ClaudeExplanationClient()
        ai_reply = client.answer_analyst_question(evidence, history, user_text)

        assistant_msg = ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=ai_reply,
            evidence_grounded=True,
        )

        return Response(
            {
                "status": "success",
                "data": {
                    "content": assistant_msg.content,
                    "role": assistant_msg.role,
                    "created_at": assistant_msg.created_at,
                    "model": "claude-3-5-sonnet",
                },
            },
            status=status.HTTP_200_OK,
        )
