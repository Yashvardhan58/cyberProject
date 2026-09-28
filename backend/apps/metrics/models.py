"""
Research Metrics and Experiment Result Models.
"""

from django.db import models


class ExperimentResult(models.Model):
    """
    Persisted evaluation outputs for Experiments E1 through E5.
    """
    EXP_CHOICES = [
        ("E1", "E1: Model Comparison (SVM vs XGBoost vs Hybrid)"),
        ("E2", "E2: Poisoning Simulation Without Governance"),
        ("E3", "E3: Poisoning Defense With Governance"),
        ("E4", "E4: Legitimate Role-Change vs Malicious Drift"),
        ("E5", "E5: FaithLens LLM Explanation Faithfulness"),
    ]

    experiment_name = models.CharField(max_length=10, choices=EXP_CHOICES, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    research_question = models.CharField(max_length=255)
    result_data = models.JSONField(help_text="Structured metrics, tables, and progression arrays")
    summary = models.TextField()
    run_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "metrics_experimentresult"
        ordering = ["experiment_name"]

    def __str__(self) -> str:
        return f"[{self.experiment_name}] {self.title}"
