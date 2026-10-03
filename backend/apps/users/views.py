"""
API Views for User Leaderboard and Profiles.
"""

from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileDetailSerializer


class UserPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 500


class UserListAPIView(generics.ListAPIView):
    """
    GET /api/v1/users/
    Returns paginated user list sorted by current risk score (Leaderboard).
    Supports ?department=, ?severity=, and ?search= filters.
    """
    serializer_class = UserProfileSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        queryset = UserProfile.objects.all().order_by("-current_risk_score", "name")
        department = self.request.query_params.get("department")
        severity = self.request.query_params.get("severity")
        search = self.request.query_params.get("search")

        if department:
            queryset = queryset.filter(department__iexact=department)
        if severity:
            queryset = queryset.filter(current_severity__iexact=severity)
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(employee_id__icontains=search)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "count": queryset.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class UserProfileDetailAPIView(APIView):
    """
    GET /api/v1/users/{identifier}/profile/
    Returns complete user profile, current risk gauge score, 30-day trajectory, and recent alerts.
    Accepts PK, employee_id, or email.
    """
    def get(self, request, identifier):
        if str(identifier).isdigit():
            user = UserProfile.objects.filter(pk=int(identifier)).first()
        else:
            user = UserProfile.objects.filter(employee_id__iexact=identifier).first()
            if not user:
                user = UserProfile.objects.filter(email__iexact=identifier).first()

        if not user:
            return Response({"status": "error", "message": f"User '{identifier}' not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

