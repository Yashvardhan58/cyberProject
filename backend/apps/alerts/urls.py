"""
URL routes for alerts app.
"""

from django.urls import path
from .views import AlertListAPIView, AlertDetailAPIView
from apps.verdicts.views import AlertVerdictSubmitAPIView

urlpatterns = [
    path("", AlertListAPIView.as_view(), name="alert-list"),
    path("<int:pk>/", AlertDetailAPIView.as_view(), name="alert-detail"),
    path("<int:alert_id>/verdict/", AlertVerdictSubmitAPIView.as_view(), name="alert-verdict-submit-alias"),
]
