"""
Serializers for Analyst Verdicts.
"""

from rest_framework import serializers
from .models import AnalystVerdict
from apps.alerts.models import Alert


class AnalystVerdictSerializer(serializers.ModelSerializer):
    """Serializer for analyst True/False Positive submissions."""
    alert_title = serializers.CharField(source="alert.title", read_only=True)
    alert_severity = serializers.CharField(source="alert.severity", read_only=True)
    user_name = serializers.CharField(source="alert.user.name", read_only=True)

    class Meta:
        model = AnalystVerdict
        fields = [
            "id",
            "alert_id",
            "alert_title",
            "alert_severity",
            "user_name",
            "verdict",
            "analyst_name",
            "analyst_note",
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = ["id", "submitted_at", "updated_at"]
