"""
Multi-Model Risk Fusion Engine.

Fuses supervised classification ($P_{\text{xgb}}$), unsupervised anomaly scoring ($S_{\text{IF}}$),
peer deviation ($D_{\text{peer}}$), user deviation ($D_{\text{user}}$), and drift suspicion ($D_{\text{drift}}$)
into a unified 0-100 composite RiskScore and severity classification.
"""

from typing import Dict, Tuple


class RiskFusionEngine:
    """
    Computes composite RiskScore and severity tiers based on research weights.
    """

    # Research Weights (Must sum to 1.0)
    W_XGB = 0.35
    W_IF = 0.25
    W_PEER = 0.20
    W_USER = 0.15
    W_DRIFT = 0.05

    # Severity Thresholds
    TIER_CRITICAL = 80.0
    TIER_HIGH = 60.0
    TIER_MEDIUM = 30.0

    @classmethod
    def calculate_risk_score(
        cls,
        p_xgb: float,
        s_if: float,
        d_peer: float,
        d_user: float,
        d_drift: float = 0.0,
    ) -> Tuple[float, str, Dict[str, float]]:
        """
        Calculate composite 0-100 RiskScore and severity tier.

        Formula:
          RiskScore = (0.35*p_xgb + 0.25*s_if + 0.20*d_peer + 0.15*d_user + 0.05*d_drift) * 100
        """
        # Clamp inputs to [0.0, 1.0] range
        p_xgb = max(0.0, min(1.0, float(p_xgb)))
        s_if = max(0.0, min(1.0, float(s_if)))
        d_peer = max(0.0, min(1.0, float(d_peer)))
        d_user = max(0.0, min(1.0, float(d_user)))
        d_drift = max(0.0, min(1.0, float(d_drift)))

        # Composite score
        weighted_sum = (
            cls.W_XGB * p_xgb +
            cls.W_IF * s_if +
            cls.W_PEER * d_peer +
            cls.W_USER * d_user +
            cls.W_DRIFT * d_drift
        )
        final_score = round(weighted_sum * 100.0, 2)

        # Classify Severity Tier
        if final_score >= cls.TIER_CRITICAL:
            severity = "CRITICAL"
        elif final_score >= cls.TIER_HIGH:
            severity = "HIGH"
        elif final_score >= cls.TIER_MEDIUM:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        breakdown = {
            "p_xgb_contribution": round(cls.W_XGB * p_xgb * 100.0, 2),
            "s_if_contribution": round(cls.W_IF * s_if * 100.0, 2),
            "d_peer_contribution": round(cls.W_PEER * d_peer * 100.0, 2),
            "d_user_contribution": round(cls.W_USER * d_user * 100.0, 2),
            "d_drift_contribution": round(cls.W_DRIFT * d_drift * 100.0, 2),
        }

        return final_score, severity, breakdown
