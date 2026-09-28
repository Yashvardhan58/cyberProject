"""
API Views for Metrics Dashboard and Experiment Results.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ExperimentResult
from .serializers import ExperimentResultSerializer


class MetricsSummaryAPIView(APIView):
    """
    GET /api/v1/metrics/
    Returns overall model evaluation metrics: Confusion Matrix, Precision, Recall, F1, and AUC.
    """
    def get(self, request):
        # Summary metrics from E1 evaluation
        metrics = {
            "overall_precision": 0.9412,
            "overall_recall": 0.9412,
            "f1_score": 0.9412,
            "auc": 0.9782,
            "confusion_matrix": {
                "tp": 16,  # True Positives
                "fp": 1,   # False Positives
                "fn": 1,   # False Negatives
                "tn": 78,  # True Negatives
            },
            "model_comparison": [
                {"model": "SVM (Baseline)", "precision": 0.8125, "recall": 0.7647, "f1": 0.7879, "auc": 0.8842},
                {"model": "XGBoost + SMOTE", "precision": 0.8947, "recall": 0.8824, "f1": 0.8885, "auc": 0.9415},
                {"model": "Hybrid Adaptive Fusion", "precision": 0.9412, "recall": 0.9412, "f1": 0.9412, "auc": 0.9782},
            ]
        }
        return Response({
            "status": "success",
            "data": metrics
        }, status=status.HTTP_200_OK)


class ExperimentResultListAPIView(generics.ListAPIView):
    """
    GET /api/v1/experiments/
    Returns list of all research experiments (E1 to E5) with structured tables and findings.
    """
    serializer_class = ExperimentResultSerializer
    queryset = ExperimentResult.objects.all().order_by("experiment_name")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "count": queryset.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)
