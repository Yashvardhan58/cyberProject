"""
API Views for Analyst Verdict Feedback.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import AnalystVerdict
from .serializers import AnalystVerdictSerializer
from apps.alerts.models import Alert


class AlertVerdictSubmitAPIView(APIView):
    """
    POST /api/v1/alerts/{id}/verdict/
    Submits or updates an analyst verdict (TP, FP, INCONCLUSIVE) on a specific alert.
    """
    def post(self, request, alert_id: int):
        alert = get_object_or_404(Alert, pk=alert_id)
        verdict_val = request.data.get("verdict")
        analyst_name = request.data.get("analyst_name", "SOC Analyst")
        analyst_note = request.data.get("analyst_note", "")

        if not verdict_val or verdict_val not in ["TP", "FP", "INCONCLUSIVE"]:
            return Response({
                "status": "error",
                "message": "Invalid verdict. Must be 'TP', 'FP', or 'INCONCLUSIVE'."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update or create verdict record
        verdict_obj, created = AnalystVerdict.objects.update_or_create(
            alert=alert,
            defaults={
                "verdict": verdict_val,
                "analyst_name": analyst_name,
                "analyst_note": analyst_note,
            }
        )

        # Update alert status and boolean flag
        alert.is_true_positive = (verdict_val == "TP")
        alert.status = "RESOLVED" if verdict_val == "TP" else "DISMISSED"
        alert.save(update_fields=["is_true_positive", "status", "updated_at"])

        serializer = AnalystVerdictSerializer(verdict_obj)
        return Response({
            "status": "success",
            "message": f"Verdict '{verdict_val}' successfully submitted for Alert #{alert_id}.",
            "data": serializer.data
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)


class VerdictListAPIView(generics.ListAPIView):
    """
    GET /api/v1/verdicts/
    Returns list of all submitted analyst verdicts for the feedback dashboard.
    Supports ?verdict= (TP|FP|INCONCLUSIVE) and ?analyst= filters.
    """
    serializer_class = AnalystVerdictSerializer

    def get_queryset(self):
        queryset = AnalystVerdict.objects.select_related("alert", "alert__user").order_by("-submitted_at")
        verdict_filter = self.request.query_params.get("verdict")
        if verdict_filter and verdict_filter.upper() != "ALL":
            queryset = queryset.filter(verdict__iexact=verdict_filter)
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
