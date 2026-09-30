"""
Serializers for Explanations and Multi-Turn Analyst Chat.
"""

from rest_framework import serializers
from .models import Explanation, ChatSession, ChatMessage


class ExplanationSerializer(serializers.ModelSerializer):
    """Serializer for AI Explanation and Celery Task Status."""
    alert_title = serializers.CharField(source="alert.title", read_only=True)
    alert_severity = serializers.CharField(source="alert.severity", read_only=True)
    user_name = serializers.CharField(source="alert.user.name", read_only=True)

    class Meta:
        model = Explanation
        fields = [
            "id",
            "alert_id",
            "alert_title",
            "alert_severity",
            "user_name",
            "evidence_hash",
            "status",
            "text",
            "explanation_text",
            "error",
            "attempts",
            "faithfulness_score",
            "model_name",
            "evidence_object",
            "created_at",
            "finished_at",
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for single chat bubble."""
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "role",
            "content",
            "evidence_grounded",
            "created_at",
        ]


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat session with embedded message history."""
    messages = ChatMessageSerializer(many=True, read_only=True)
    alert_title = serializers.CharField(source="alert.title", read_only=True)
    alert_severity = serializers.CharField(source="alert.severity", read_only=True)
    user_name = serializers.CharField(source="alert.user.name", read_only=True)

    class Meta:
        model = ChatSession
        fields = [
            "id",
            "session_token",
            "alert_id",
            "alert_title",
            "alert_severity",
            "user_name",
            "analyst_name",
            "messages",
            "created_at",
            "updated_at",
        ]
