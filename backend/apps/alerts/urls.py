"""
URL routes for alerts app.
"""

from django.urls import path
from .views import AlertListAPIView, AlertDetailAPIView

urlpatterns = [
    path("", AlertListAPIView.as_view(), name="alert-list"),
    path("<int:pk>/", AlertDetailAPIView.as_view(), name="alert-detail"),
]
