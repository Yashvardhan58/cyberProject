"""
Security Analyst Feedback and Alert Verdict Models.
"""

from django.db import models
from apps.alerts.models import Alert


class AnalystVerdict(models.Model):
    """
    Human analyst feedback on alert accuracy (True Positive / False Positive)
    for closed-loop model evaluation.
    """
    VERDICT_CHOICES = [
        ("TP", "True Positive (Confirmed Threat)"),
        ("FP", "False Positive (Benign Activity)"),
        ("INCONCLUSIVE", "Inconclusive / Requires Further Investigation"),
    ]

    alert = models.OneToOneField(Alert, on_delete=models.CASCADE, related_name="verdict")
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES, db_index=True)
    analyst_name = models.CharField(max_length=150, default="SOC Analyst")
    analyst_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "verdicts_analystverdict"
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"Verdict on Alert #{self.alert_id}: {self.verdict} ({self.analyst_name})"
