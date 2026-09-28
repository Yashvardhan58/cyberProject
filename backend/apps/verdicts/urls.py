"""
URL routes for verdicts app.
"""

from django.urls import path
from .views import VerdictListAPIView, AlertVerdictSubmitAPIView

urlpatterns = [
    path("", VerdictListAPIView.as_view(), name="verdict-list"),
    path("alerts/<int:alert_id>/verdict/", AlertVerdictSubmitAPIView.as_view(), name="alert-verdict-submit"),
]
