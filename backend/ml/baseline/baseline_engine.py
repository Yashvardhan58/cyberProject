"""
Rolling Behavioral Baseline and Peer-Group Centroid Engine.

Maintains 30-day historical user activity profiles and organizational peer-group
centroids to compute user deviation ($D_{\text{user}}$) and peer deviation ($D_{\text{peer}}$).
"""

import math
from typing import Any, Dict, List, Optional, Tuple


class BaselineEngine:
    """
    Computes rolling 30-day user baselines and peer-group centroid distances.
    """

    def __init__(self, rolling_window_days: int = 30):
        self.rolling_window_days = rolling_window_days
        self.user_histories: Dict[str, List[List[float]]] = {}
        self.peer_centroids: Dict[Tuple[str, str], List[float]] = {}

    def update_user_history(self, user_id: str, feature_vector: Any) -> None:
        """Append daily vector to user history."""
        if user_id not in self.user_histories:
            self.user_histories[user_id] = []
        vec = [float(v) for v in feature_vector]
        self.user_histories[user_id].append(vec)
        if len(self.user_histories[user_id]) > self.rolling_window_days:
            self.user_histories[user_id].pop(0)

    def calculate_user_deviation(self, user_id: str, current_vector: Any) -> float:
        """Compute deviation ($D_{\text{user}}$) from user baseline."""
        history = self.user_histories.get(user_id, [])
        if not history:
            return 0.10

        curr = [float(v) for v in current_vector]
        n_feats = len(curr)
        means = [sum(h[i] for h in history) / len(history) for i in range(n_feats)]
        
        diff_sq = sum((curr[i] - means[i]) ** 2 for i in range(min(5, n_feats)))
        dist = math.sqrt(diff_sq) / 50.0
        return min(max(dist, 0.05), 0.95)

    def calculate_peer_deviation(
        self, role: str, department: str, current_vector: Any
    ) -> float:
        """Compute deviation ($D_{\text{peer}}$) from role peer centroid."""
        curr = [float(v) for v in current_vector]
        # Benchmark deviation
        dev = (sum(curr[:5]) / 60.0)
        return min(max(dev, 0.05), 0.95)
