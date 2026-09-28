"""
Serializers for Metrics and Research Experiment Results.
"""

from rest_framework import serializers
from .models import ExperimentResult


class ExperimentResultSerializer(serializers.ModelSerializer):
    """Serializer for E1 through E5 experiment result tables."""
    class Meta:
        model = ExperimentResult
        fields = [
            "id",
            "experiment_name",
            "title",
            "research_question",
            "result_data",
            "summary",
            "run_at",
        ]
