"""
User and Peer Group Models for Adaptive UEBA.
"""

from django.db import models


class PeerGroup(models.Model):
    """
    Organizational peer group clustered by job role and department.
    """
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    centroid_vector = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_peergroup"
        unique_together = ("role", "department")
        ordering = ["department", "role"]

    def __str__(self) -> str:
        return f"{self.department} - {self.role}"


class UserProfile(models.Model):
    """
    Employee user profile monitored by the UEBA intelligence layer.
    """
    SEVERITY_CHOICES = [
        ("LOW", "Low Risk (0-30)"),
        ("MEDIUM", "Medium Risk (31-60)"),
        ("HIGH", "High Risk (61-80)"),
        ("CRITICAL", "Critical Risk (81-100)"),
    ]

    employee_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    peer_group = models.ForeignKey(
        PeerGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="members"
    )
    current_risk_score = models.FloatField(default=0.0)
    current_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="LOW")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_userprofile"
        ordering = ["-current_risk_score", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.employee_id}) - Score: {self.current_risk_score}"
