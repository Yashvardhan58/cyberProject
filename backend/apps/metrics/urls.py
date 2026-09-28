"""
URL routes for metrics and experiments app.
"""

from django.urls import path
from .views import MetricsSummaryAPIView, ExperimentResultListAPIView

urlpatterns = [
    path("summary/", MetricsSummaryAPIView.as_view(), name="metrics-summary"),
    path("experiments/", ExperimentResultListAPIView.as_view(), name="experiment-list"),
]
