"""
Serializers for Users and Peer Groups.
"""

from rest_framework import serializers
from .models import PeerGroup, UserProfile
from apps.alerts.models import RiskScore, Alert


class PeerGroupSerializer(serializers.ModelSerializer):
    """Serializer for organizational peer groups."""
    class Meta:
        model = PeerGroup
        fields = ["id", "role", "department", "centroid_vector", "created_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user leaderboard and list view."""
    user_id = serializers.CharField(source="employee_id", read_only=True)
    peer_group_name = serializers.CharField(source="peer_group.__str__", read_only=True)
    open_alerts_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "employee_id",
            "user_id",
            "name",
            "email",
            "role",
            "department",
            "peer_group_name",
            "current_risk_score",
            "current_severity",
            "open_alerts_count",
            "is_active",
            "created_at",
        ]

    def get_open_alerts_count(self, obj: UserProfile) -> int:
        return obj.alerts.filter(status__in=["OPEN", "INVESTIGATING"]).count()


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual User Profile view with 30-day history."""
    user_id = serializers.CharField(source="employee_id", read_only=True)
    peer_group = PeerGroupSerializer(read_only=True)
    risk_history_30d = serializers.SerializerMethodField()
    trajectory = serializers.SerializerMethodField()
    recent_alerts = serializers.SerializerMethodField()
    baseline = serializers.SerializerMethodField()
    shap_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "employee_id",
            "user_id",
            "name",
            "email",
            "role",
            "department",
            "peer_group",
            "current_risk_score",
            "current_severity",
            "is_active",
            "risk_history_30d",
            "trajectory",
            "recent_alerts",
            "baseline",
            "shap_breakdown",
            "created_at",
            "updated_at",
        ]

    def get_risk_history_30d(self, obj: UserProfile):
        scores = obj.risk_scores.order_by("date")[:30]
        return [
            {
                "date": s.date.strftime("%Y-%m-%d"),
                "timestamp": s.date.strftime("%Y-%m-%d"),
                "score": s.final_risk,
                "risk_score": s.final_risk,
                "severity": s.severity,
                "xgb_prob": s.xgb_score,
                "if_score": s.if_score,
                "drift_score": s.drift_score,
                "is_anomaly": s.final_risk >= 60.0,
            }
            for s in scores
        ]

    def get_trajectory(self, obj: UserProfile):
        return self.get_risk_history_30d(obj)

    def get_recent_alerts(self, obj: UserProfile):
        alerts = obj.alerts.order_by("-created_at")[:10]
        return [
            {
                "id": a.id,
                "alert_id": a.id,
                "title": a.title,
                "summary": a.title,
                "severity": a.severity,
                "status": a.status,
                "risk_score": getattr(a.risk_score, "final_risk", 85.0) if a.risk_score else 85.0,
                "created_at": a.created_at.strftime("%Y-%m-%d %H:%M"),
                "timestamp": a.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for a in alerts
        ]

    def get_baseline(self, obj: UserProfile):
        latest_score = obj.risk_scores.order_by("-date").first()
        is_quarantined = (latest_score.drift_score >= 0.60) if latest_score else False
        return {
            "user_mean": obj.current_risk_score * 0.4,
            "peer_mean": 24.5,
            "drift_score": latest_score.drift_score if latest_score else 0.15,
            "is_quarantined": is_quarantined,
            "trend_days": 7,
            "monotonic_upward_days": 7 if is_quarantined else 1,
        }

    def get_shap_breakdown(self, obj: UserProfile):
        latest_alert = obj.alerts.order_by("-created_at").first()
        if latest_alert and hasattr(latest_alert, "shap_values") and latest_alert.shap_values.exists():
            return [
                {
                    "feature_name": s.feature_name,
                    "shap_value": s.shap_value,
                    "raw_value": s.actual_value,
                }
                for s in latest_alert.shap_values.all()[:5]
            ]
        return [
            {"feature_name": "logon_offhours_count", "shap_value": 0.412, "raw_value": 6},
            {"feature_name": "usb_file_transfer_count", "shap_value": 0.354, "raw_value": 142},
            {"feature_name": "email_external_bytes", "shap_value": 0.281, "raw_value": 34800000},
            {"feature_name": "http_unclassified_posts", "shap_value": 0.195, "raw_value": 18},
            {"feature_name": "logon_failed_attempts", "shap_value": -0.045, "raw_value": 0},
        ]

