"""
Risk Scores, Threat Alerts, and SHAP Attribution Models.
"""

from django.db import models
from apps.users.models import UserProfile


class RiskScore(models.Model):
    """
    Daily composite RiskScore breakdown computed by the RiskFusionEngine.
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="risk_scores")
    date = models.DateField(db_index=True)
    
    # Model Component Probabilities / Scores (0.0 to 1.0)
    xgb_score = models.FloatField(help_text="P_xgb (XGBoost malicious probability)")
    if_score = models.FloatField(help_text="S_IF (Isolation Forest anomaly score)")
    peer_score = models.FloatField(help_text="D_peer (Distance from peer centroid)")
    user_score = models.FloatField(help_text="D_user (Distance from personal baseline)")
    drift_score = models.FloatField(default=0.0, help_text="D_drift (Drift suspicion score)")
    
    # Composite Fused Score (0.0 to 100.0)
    final_risk = models.FloatField(db_index=True, help_text="Composite 0-100 score")
    severity = models.CharField(max_length=20, default="LOW")
    component_breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alerts_riskscore"
        unique_together = ("user", "date")
        ordering = ["-date", "-final_risk"]

    def __str__(self) -> str:
        return f"{self.user.name} ({self.date}) - Score: {self.final_risk}"


class Alert(models.Model):
    """
    Actionable security incident alert raised when RiskScore exceeds threshold.
    """
    SEVERITY_CHOICES = [
        ("LOW", "Low Risk (0-30)"),
        ("MEDIUM", "Medium Risk (31-60)"),
        ("HIGH", "High Risk (61-80)"),
        ("CRITICAL", "Critical Risk (81-100)"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open (New Alert)"),
        ("INVESTIGATING", "Under Investigation"),
        ("RESOLVED", "Resolved"),
        ("DISMISSED", "Dismissed"),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="alerts")
    risk_score = models.ForeignKey(RiskScore, on_delete=models.CASCADE, related_name="alerts")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN", db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    top_feature_summary = models.CharField(max_length=255, blank=True)
    is_true_positive = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alerts_alert"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.user.name} - {self.title} ({self.created_at.strftime('%Y-%m-%d')})"


class SHAPValue(models.Model):
    """
    Individual feature contribution extracted via TreeSHAP for an alert.
    """
    DIRECTION_CHOICES = [
        ("positive", "Positive (Pushed score up)"),
        ("negative", "Negative (Pushed score down)"),
    ]

    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name="shap_values")
    feature_name = models.CharField(max_length=150)
    shap_value = models.FloatField()
    actual_value = models.FloatField()
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default="positive")
    rank = models.IntegerField(help_text="Importance rank 1 to 5")

    class Meta:
        db_table = "alerts_shapvalue"
        ordering = ["alert", "rank"]
        unique_together = ("alert", "rank")

    def __str__(self) -> str:
        return f"Rank #{self.rank}: {self.feature_name} (SHAP: {self.shap_value})"
