"""
Contamination-Resistant Baseline Governance Engine.

Primary research contribution: Defends adaptive UEBA systems against slow-escalation
baseline poisoning attacks through a four-stage weekly governance validation check.
"""

from typing import Dict, List, Optional, Tuple, Union


class BaselineGovernanceEngine:
    """
    Four-stage baseline governance engine to suppress poisoned baseline updates.
    """

    SUSPICION_THRESHOLD = 0.60
    MONOTONIC_WINDOW_DAYS = 7

    def __init__(self, suspicion_threshold: float = 0.60):
        self.suspicion_threshold = suspicion_threshold

    def evaluate_drift_rate(
        self, historical_deviations: List[float]
    ) -> Tuple[bool, float]:
        """Stage 1: Drift Rate Monitoring."""
        if len(historical_deviations) < 3:
            return True, 0.10

        diffs = [historical_deviations[i] - historical_deviations[i-1] for i in range(1, len(historical_deviations))]
        mean_rate = sum(diffs) / len(diffs)
        rate_score = min(max(mean_rate * 5.0, 0.0), 1.0)
        passed = rate_score < 0.50
        return passed, rate_score

    def evaluate_peer_anchor_divergence(
        self, user_deviation: float, peer_deviation: float
    ) -> Tuple[bool, float]:
        """Stage 2: Peer-Anchor Divergence Check."""
        divergence = max(0.0, user_deviation - peer_deviation)
        divergence_score = min(max(divergence * 1.5, 0.0), 1.0)
        passed = divergence_score < 0.45
        return passed, divergence_score

    def evaluate_monotonic_trend(
        self, historical_risk_scores: List[float]
    ) -> Tuple[bool, float]:
        """Stage 3: Monotonic Trend Detection (7-Day Window)."""
        if len(historical_risk_scores) < 4:
            return True, 0.10

        window = historical_risk_scores[-self.MONOTONIC_WINDOW_DAYS:]
        diffs = [window[i] - window[i-1] for i in range(1, len(window))]
        positive_steps = sum(1 for d in diffs if d >= 0)
        monotonicity_ratio = positive_steps / len(diffs)
        
        trend_score = min(max(monotonicity_ratio, 0.0), 1.0)
        passed = trend_score < 0.75
        return passed, trend_score

    def run_governance_check(
        self,
        user_id: str,
        historical_deviations: List[float],
        user_deviation: float,
        peer_deviation: float,
        recent_risk_scores: List[float],
    ) -> Dict[str, Union[str, float, bool]]:
        """Stage 4: Combined Drift Suspicion Scoring and Final Verdict."""
        stg1_pass, stg1_score = self.evaluate_drift_rate(historical_deviations)
        stg2_pass, stg2_score = self.evaluate_peer_anchor_divergence(user_deviation, peer_deviation)
        stg3_pass, stg3_score = self.evaluate_monotonic_trend(recent_risk_scores)

        # Composite suspicion score
        suspicion_score = round(
            0.35 * stg1_score + 0.40 * stg2_score + 0.25 * stg3_score, 4
        )

        should_suppress = suspicion_score >= self.suspicion_threshold
        verdict = "SUPPRESS" if should_suppress else "ALLOW"

        reason = "Normal behavioral drift"
        if should_suppress:
            reasons = []
            if not stg1_pass:
                reasons.append("Excessive drift acceleration")
            if not stg2_pass:
                reasons.append("Unilateral peer-anchor divergence")
            if not stg3_pass:
                reasons.append("Persistent 7-day monotonic escalation")
            reason = "; ".join(reasons) if reasons else "High cumulative suspicion score"

        return {
            "user_id": user_id,
            "verdict": verdict,
            "is_suppressed": should_suppress,
            "suspicion_score": suspicion_score,
            "reason": reason,
            "stage_1_drift_rate_score": round(stg1_score, 4),
            "stage_2_peer_divergence_score": round(stg2_score, 4),
            "stage_3_monotonic_trend_score": round(stg3_score, 4),
        }
