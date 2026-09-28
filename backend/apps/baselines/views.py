"""
API Views for Baselines and Governance Logs.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from .models import GovernanceLog, UserBaseline
from .serializers import GovernanceLogSerializer, UserBaselineSerializer


class GovernanceLogListAPIView(generics.ListAPIView):
    """
    GET /api/v1/baselines/governance/
    Returns list of baseline governance decisions.
    Supports ?verdict= (ALLOW|SUPPRESS) and ?user_id= filters.
    """
    serializer_class = GovernanceLogSerializer

    def get_queryset(self):
        queryset = GovernanceLog.objects.select_related("user").order_by("-check_date", "-suspicion_score")
        verdict = self.request.query_params.get("verdict")
        user_id = self.request.query_params.get("user_id")

        if verdict and verdict.upper() != "ALL":
            queryset = queryset.filter(verdict__iexact=verdict)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

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


class BaselineActivityStatsAPIView(APIView):
    """
    GET /api/v1/baselines/stats/
    Returns weekly baseline activity (Allowed vs. Suppressed updates) for Admin Metrics bar chart.
    """
    def get(self, request):
        total_checks = GovernanceLog.objects.count()
        suppressed_count = GovernanceLog.objects.filter(verdict="SUPPRESS").count()
        allowed_count = GovernanceLog.objects.filter(verdict="ALLOW").count()

        # Weekly Activity Breakdown (Sample 4 weeks progression)
        weekly_series = [
            {"week": "Week 1", "allowed": 10, "suppressed": 0},
            {"week": "Week 2", "allowed": 9, "suppressed": 1},
            {"week": "Week 3", "allowed": 8, "suppressed": 2},
            {"week": "Week 4", "allowed": 8, "suppressed": 2},
        ]

        return Response({
            "status": "success",
            "data": {
                "total_governance_checks": total_checks,
                "allowed_updates": allowed_count,
                "suppressed_updates": suppressed_count,
                "suppression_rate": round(suppressed_count / (total_checks + 1e-5), 4),
                "weekly_activity": weekly_series,
            }
        }, status=status.HTTP_200_OK)
