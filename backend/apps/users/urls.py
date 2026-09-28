"""
URL routes for users app.
"""

from django.urls import path
from .views import UserListAPIView, UserProfileDetailAPIView

urlpatterns = [
    path("", UserListAPIView.as_view(), name="user-list"),
    path("<str:identifier>/profile/", UserProfileDetailAPIView.as_view(), name="user-profile-detail"),
    path("<str:identifier>/", UserProfileDetailAPIView.as_view(), name="user-detail"),
]
