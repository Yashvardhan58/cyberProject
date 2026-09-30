"""
URL routes for explanations and analyst chat app.
"""

from django.urls import path
from .views import (
    ExplanationListCreateAPIView,
    ExplanationDetailAPIView,
    AlertChatInitAPIView,
    ChatSessionDetailAPIView,
)

urlpatterns = [
    # Top-level Explanation REST Endpoints
    path("", ExplanationListCreateAPIView.as_view(), name="explanation-list-create"),
    path("<int:id>/", ExplanationDetailAPIView.as_view(), name="explanation-detail"),
    
    # Alert-scoped endpoints (backwards-compatible)
    path("alerts/<int:alert_id>/explanation/", ExplanationListCreateAPIView.as_view(), name="alert-explanation"),
    path("alerts/<int:alert_id>/chat/init/", AlertChatInitAPIView.as_view(), name="alert-chat-init"),
    path("sessions/<str:session_token>/", ChatSessionDetailAPIView.as_view(), name="chat-session-detail"),
]
