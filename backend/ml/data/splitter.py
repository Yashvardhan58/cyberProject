"""
Dataset Chronological Splitting Module.

Enforces strict time-based train/test splitting (no random shuffle) to ensure
zero temporal data leakage for time-series insider threat detection.
"""

from typing import Tuple
import pandas as pd


class TimeSeriesSplitter:
    """
    Splits dataset chronologically based on record date.
    """

    @staticmethod
    def split_chronological(
        df: pd.DataFrame,
        date_column: str = "date",
        train_ratio: float = 0.80,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split a DataFrame chronologically into train and test sets.

        Args:
            df: Input feature matrix DataFrame.
            date_column: Name of date/timestamp column.
            train_ratio: Proportion of chronological time for training (default: 0.80).

        Returns:
            Tuple of (train_df, test_df).
        """
        if df.empty:
            raise ValueError("Cannot split an empty DataFrame.")

        # Ensure date sorting
        sorted_df = df.sort_values(by=date_column).copy()
        
        # Get unique dates in order
        unique_dates = sorted_df[date_column].drop_duplicates().tolist()
        split_point = int(len(unique_dates) * train_ratio)
        cutoff_date = unique_dates[split_point]

        train_df = sorted_df[sorted_df[date_column] < cutoff_date].copy()
        test_df = sorted_df[sorted_df[date_column] >= cutoff_date].copy()

        return train_df, test_df
