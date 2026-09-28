"""
URL routes for explanations and analyst chat app.
"""

from django.urls import path
from .views import AlertExplanationAPIView, AlertChatInitAPIView, ChatSessionDetailAPIView

urlpatterns = [
    path("alerts/<int:alert_id>/explanation/", AlertExplanationAPIView.as_view(), name="alert-explanation"),
    path("alerts/<int:alert_id>/chat/init/", AlertChatInitAPIView.as_view(), name="alert-chat-init"),
    path("sessions/<str:session_token>/", ChatSessionDetailAPIView.as_view(), name="chat-session-detail"),
]
