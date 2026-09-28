"""
Serializers for Behavioral Baselines and Governance Logs.
"""

from rest_framework import serializers
from .models import UserBaseline, GovernanceLog


class GovernanceLogSerializer(serializers.ModelSerializer):
    """Serializer for 4-stage governance decision logs."""
    user_name = serializers.CharField(source="user.name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)

    class Meta:
        model = GovernanceLog
        fields = [
            "id",
            "user_id",
            "employee_id",
            "user_name",
            "user_role",
            "check_date",
            "stage_1_drift_rate_score",
            "stage_2_peer_divergence_score",
            "stage_3_monotonic_trend_score",
            "suspicion_score",
            "verdict",
            "reason",
            "action_taken",
            "created_at",
        ]


class UserBaselineSerializer(serializers.ModelSerializer):
    """Serializer for user 30-day baseline vectors."""
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = UserBaseline
        fields = [
            "id",
            "user_id",
            "user_name",
            "baseline_date",
            "feature_vector",
            "is_suppressed",
            "suppression_reason",
            "created_at",
        ]
