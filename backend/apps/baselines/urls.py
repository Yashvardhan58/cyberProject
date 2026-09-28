"""
URL routes for baselines app.
"""

from django.urls import path
from .views import GovernanceLogListAPIView, BaselineActivityStatsAPIView

urlpatterns = [
    path("governance/", GovernanceLogListAPIView.as_view(), name="governance-log-list"),
    path("stats/", BaselineActivityStatsAPIView.as_view(), name="baseline-stats"),
]
