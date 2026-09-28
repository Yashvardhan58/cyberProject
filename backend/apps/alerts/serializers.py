"""
Serializers for Risk Scores, Threat Alerts, and SHAP Attributions.
"""

from rest_framework import serializers
from .models import RiskScore, Alert, SHAPValue
from apps.users.serializers import UserProfileSerializer


class SHAPValueSerializer(serializers.ModelSerializer):
    """Serializer for individual SHAP feature impact."""
    class Meta:
        model = SHAPValue
        fields = ["rank", "feature_name", "shap_value", "actual_value", "direction"]


class RiskScoreSerializer(serializers.ModelSerializer):
    """Serializer for composite RiskScore breakdown."""
    class Meta:
        model = RiskScore
        fields = [
            "id",
            "date",
            "final_risk",
            "severity",
            "xgb_score",
            "if_score",
            "peer_score",
            "user_score",
            "drift_score",
            "component_breakdown",
            "created_at",
        ]


class AlertListSerializer(serializers.ModelSerializer):
    """Serializer for Alert feed and incident timeline rows."""
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)
    user_id = serializers.CharField(source="user.employee_id", read_only=True)
    risk_score = serializers.SerializerMethodField()
    risk_score_val = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source="created_at", read_only=True)
    top_contributing_feature = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = [
            "id",
            "user_id",
            "employee_id",
            "user_name",
            "user_role",
            "title",
            "severity",
            "status",
            "risk_score",
            "risk_score_val",
            "top_contributing_feature",
            "top_feature_summary",
            "is_true_positive",
            "timestamp",
            "created_at",
        ]

    def get_risk_score(self, obj: Alert) -> float:
        if obj.risk_score:
            return round(obj.risk_score.final_risk, 1)
        return 85.0

    def get_risk_score_val(self, obj: Alert) -> float:
        return self.get_risk_score(obj)

    def get_top_contributing_feature(self, obj: Alert) -> str:
        if hasattr(obj, "shap_values") and obj.shap_values.exists():
            top = obj.shap_values.order_by("-shap_value").first()
            if top:
                return top.feature_name
        return obj.top_feature_summary or "logon_offhours_count"



class AlertDetailSerializer(serializers.ModelSerializer):
    """Detailed Alert serializer with SHAP top-5 breakdown and explanation."""
    user = UserProfileSerializer(read_only=True)
    user_id = serializers.CharField(source="user.employee_id", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)
    risk_score = RiskScoreSerializer(read_only=True)
    final_risk_score = serializers.SerializerMethodField()
    top_contributing_feature = serializers.SerializerMethodField()
    shap_values = SHAPValueSerializer(many=True, read_only=True)
    explanation_text = serializers.SerializerMethodField()
    faithfulness_score = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = [
            "id",
            "title",
            "description",
            "severity",
            "status",
            "is_true_positive",
            "user",
            "user_id",
            "user_name",
            "employee_id",
            "risk_score",
            "final_risk_score",
            "top_contributing_feature",
            "shap_values",
            "explanation_text",
            "faithfulness_score",
            "created_at",
            "updated_at",
        ]

    def get_final_risk_score(self, obj: Alert) -> float:
        if obj.risk_score:
            return round(obj.risk_score.final_risk, 1)
        return 85.0

    def get_top_contributing_feature(self, obj: Alert) -> str:
        if hasattr(obj, "shap_values") and obj.shap_values.exists():
            top = obj.shap_values.order_by("-shap_value").first()
            if top:
                return top.feature_name
        return obj.top_feature_summary or "file_copy_to_usb_bytes"

    def get_explanation_text(self, obj: Alert) -> str:
        if hasattr(obj, "explanation") and obj.explanation:
            return obj.explanation.explanation_text
        return "Explanation pending generation."

    def get_faithfulness_score(self, obj: Alert) -> float:
        if hasattr(obj, "explanation") and obj.explanation:
            return obj.explanation.faithfulness_score
        return 0.95

