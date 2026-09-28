"""
API Views for Threat Alerts and SHAP Explanations.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Alert
from .serializers import AlertListSerializer, AlertDetailSerializer


class AlertListAPIView(generics.ListAPIView):
    """
    GET /api/v1/alerts/
    Returns paginated list of security alerts.
    Supports filters: ?severity= (CRITICAL|HIGH|MEDIUM|LOW), ?status=, and ?search=.
    """
    serializer_class = AlertListSerializer

    def get_queryset(self):
        queryset = Alert.objects.select_related("user", "risk_score").order_by("-created_at")
        severity = self.request.query_params.get("severity")
        status_param = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        user_id = self.request.query_params.get("user_id") or self.request.query_params.get("employee_id")

        if user_id:
            if str(user_id).isdigit():
                queryset = queryset.filter(user_id=int(user_id))
            else:
                queryset = queryset.filter(user__employee_id__iexact=user_id)
        if severity and severity.upper() != "ALL":
            queryset = queryset.filter(severity__iexact=severity)
        if status_param and status_param.upper() != "ALL":
            queryset = queryset.filter(status__iexact=status_param)
        if search:
            queryset = queryset.filter(user__name__icontains=search) | queryset.filter(title__icontains=search)

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


class AlertDetailAPIView(APIView):
    """
    GET /api/v1/alerts/{id}/
    Returns detailed alert record including top-5 SHAP values, risk scores, and explanation.
    """
    def get(self, request, pk: int):
        alert = get_object_or_404(
            Alert.objects.select_related("user", "risk_score").prefetch_related("shap_values"),
            pk=pk
        )
        serializer = AlertDetailSerializer(alert)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
