"""
Behavioral Baselines and Governance Decision Log Models.
"""

from django.db import models
from apps.users.models import UserProfile


class UserBaseline(models.Model):
    """
    Rolling 30-day historical behavioral baseline vector for an employee.
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="baselines")
    baseline_date = models.DateField(db_index=True)
    feature_vector = models.JSONField(help_text="30-day rolling mean behavioral vector")
    is_suppressed = models.BooleanField(default=False, help_text="True if governance suppressed this update")
    suppression_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "baselines_userbaseline"
        ordering = ["-baseline_date"]
        unique_together = ("user", "baseline_date")

    def __str__(self) -> str:
        status = "SUPPRESSED" if self.is_suppressed else "ACTIVE"
        return f"{self.user.name} ({self.baseline_date}) - {status}"


class GovernanceLog(models.Model):
    """
    Audit log of 4-stage governance checks evaluating baseline update contamination.
    """
    VERDICT_CHOICES = [
        ("ALLOW", "Allowed (Normal Operational Drift)"),
        ("SUPPRESS", "Suppressed (Contamination / Poisoning Detected)"),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="governance_logs")
    check_date = models.DateField(db_index=True)
    stage_1_drift_rate_score = models.FloatField(default=0.0)
    stage_2_peer_divergence_score = models.FloatField(default=0.0)
    stage_3_monotonic_trend_score = models.FloatField(default=0.0)
    suspicion_score = models.FloatField(help_text="Composite suspicion score (0.0 to 1.0)")
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, db_index=True)
    reason = models.CharField(max_length=255)
    action_taken = models.CharField(max_length=100, default="BASELINE_FROZEN")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "baselines_governancelog"
        ordering = ["-check_date", "-suspicion_score"]

    def __str__(self) -> str:
        return f"[{self.verdict}] {self.user.name} - Suspicion: {self.suspicion_score} ({self.check_date})"
