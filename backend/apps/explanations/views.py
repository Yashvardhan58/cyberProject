"""
API Views for Explanations and Interactive Analyst Chatbot.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from datetime import datetime, timezone

from .models import Explanation, ChatSession, ChatMessage
from .serializers import ExplanationSerializer, ChatSessionSerializer, ChatMessageSerializer
from .evidence_builder import EvidenceBuilder
from .llm_client import ClaudeExplanationClient
from apps.alerts.models import Alert


class AlertExplanationAPIView(APIView):
    """
    GET /api/v1/alerts/{id}/explanation/
    Fetch or generate the evidence-grounded LLM explanation for an alert.
    """
    def get(self, request, alert_id: int):
        alert = get_object_or_404(Alert, pk=alert_id)
        
        explanation = getattr(alert, "explanation", None)
        if not explanation:
            # Generate dynamically on first request
            evidence = EvidenceBuilder.build_alert_evidence(alert)
            client = ClaudeExplanationClient()
            result = client.generate_alert_explanation(evidence)

            explanation = Explanation.objects.create(
                alert=alert,
                evidence_object=evidence,
                explanation_text=result["explanation_text"],
                faithfulness_score=result["faithfulness_score"],
                model_name=result["model_name"],
            )

        serializer = ExplanationSerializer(explanation)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, alert_id: int):
        """Force regenerate explanation."""
        alert = get_object_or_404(Alert, pk=alert_id)
        evidence = EvidenceBuilder.build_alert_evidence(alert)
        client = ClaudeExplanationClient()
        result = client.generate_alert_explanation(evidence)

        explanation, _ = Explanation.objects.update_or_create(
            alert=alert,
            defaults={
                "evidence_object": evidence,
                "explanation_text": result["explanation_text"],
                "faithfulness_score": result["faithfulness_score"],
                "model_name": result["model_name"],
            }
        )
        serializer = ExplanationSerializer(explanation)
        return Response({
            "status": "success",
            "message": "Explanation successfully regenerated.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AlertChatInitAPIView(APIView):
    """
    POST /api/v1/alerts/{id}/chat/init/
    Initialize or resume a chat session for an alert.
    """
    def post(self, request, alert_id: int):
        alert = get_object_or_404(Alert, pk=alert_id)
        analyst_name = request.data.get("analyst_name", "Security Analyst")

        # Find existing session or create new
        session = ChatSession.objects.filter(alert=alert).first()
        if not session:
            token = f"sess_{alert.id}_{int(datetime.now(timezone.utc).timestamp())}"
            session = ChatSession.objects.create(
                alert=alert,
                analyst_name=analyst_name,
                session_token=token
            )
            # Add initial system intro / explanation
            explanation = getattr(alert, "explanation", None)
            intro_text = explanation.explanation_text if explanation else f"Alert #{alert.id} context loaded. You can ask follow-up questions."
            ChatMessage.objects.create(
                session=session,
                role="assistant",
                content=intro_text,
                evidence_grounded=True
            )

        serializer = ChatSessionSerializer(session)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ChatSessionDetailAPIView(APIView):
    """
    GET & POST /api/v1/chat/{session_token}/
    Send follow-up questions and retrieve conversation transcript.
    """
    def get(self, request, session_token: str):
        session = get_object_or_404(ChatSession, session_token=session_token)
        serializer = ChatSessionSerializer(session)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, session_token: str):
        session = get_object_or_404(ChatSession, session_token=session_token)
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return Response({
                "status": "error",
                "message": "Message content cannot be empty."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 1. Store user question
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=user_message,
            evidence_grounded=True
        )

        # 2. Build evidence and history for LLM
        evidence = EvidenceBuilder.build_alert_evidence(session.alert)
        history = [
            {"role": m.role, "content": m.content}
            for m in session.messages.order_by("created_at")
        ]

        # 3. Generate response via Claude client
        client = ClaudeExplanationClient()
        ai_reply = client.answer_analyst_question(evidence, history, user_message)

        # 4. Store assistant response
        assistant_msg = ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=ai_reply,
            evidence_grounded=True
        )

        return Response({
            "status": "success",
            "data": ChatMessageSerializer(assistant_msg).data
        }, status=status.HTTP_200_OK)
