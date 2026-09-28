"""
Structured Evidence Object Builder for Claude LLM.

Constructs comprehensive, faithful JSON evidence objects combining SHAP top-5 features,
risk score breakdowns, and 7-day trend analysis for evidence-constrained explanation prompts.
"""

from typing import Any, Dict, List
from apps.alerts.models import Alert


class EvidenceBuilder:
    """
    Assembles evidence payloads for LLM grounding.
    """

    @staticmethod
    def build_alert_evidence(alert: Alert) -> Dict[str, Any]:
        """
        Build a complete structured evidence object for a given Alert.

        Args:
            alert: Alert model instance.

        Returns:
            Dictionary containing structured evidence.
        """
        user = alert.user
        risk_score = alert.risk_score

        # 1. User & Organizational Context
        user_context = {
            "employee_id": user.employee_id,
            "name": user.name,
            "role": user.role,
            "department": user.department,
        }

        # 2. Risk Score & Component Breakdown
        score_context = {
            "composite_risk_score": risk_score.final_risk,
            "severity_tier": alert.severity,
            "components": {
                "xgboost_malicious_probability": risk_score.xgb_score,
                "isolation_forest_anomaly_score": risk_score.if_score,
                "peer_group_deviation": risk_score.peer_score,
                "personal_baseline_deviation": risk_score.user_score,
                "drift_suspicion_score": risk_score.drift_score,
            }
        }

        # 3. Top-5 SHAP Features
        shap_records = alert.shap_values.order_by("rank")[:5]
        top_shap_features = [
            {
                "rank": s.rank,
                "feature": s.feature_name,
                "shap_impact": s.shap_value,
                "observed_value": s.actual_value,
                "direction": s.direction,
            }
            for s in shap_records
        ]

        # 4. 7-Day Historical Risk Trend
        recent_scores = list(user.risk_scores.order_by("-date")[:7])
        recent_scores.reverse()
        trend_progression = [
            {"date": s.date.strftime("%Y-%m-%d"), "score": s.final_risk}
            for s in recent_scores
        ]

        trend_summary = "Stable"
        if len(trend_progression) >= 3:
            first_val = trend_progression[0]["score"]
            last_val = trend_progression[-1]["score"]
            if last_val - first_val > 20:
                trend_summary = f"Significant escalation from {first_val} to {last_val} over recent days."
            elif last_val - first_val > 5:
                trend_summary = f"Gradual upward drift from {first_val} to {last_val}."

        evidence_payload = {
            "alert_id": alert.id,
            "alert_title": alert.title,
            "timestamp": alert.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "employee_context": user_context,
            "risk_evaluation": score_context,
            "top_contributing_features_shap": top_shap_features,
            "seven_day_trend": {
                "progression": trend_progression,
                "summary": trend_summary,
            }
        }

        return evidence_payload
