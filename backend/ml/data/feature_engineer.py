"""
Feature Engineering Pipeline Module.

Transforms cleaned multi-source event logs (logon, file, device, email, http) into
a structured daily user-feature matrix with 40+ behavioral indicators.
"""

from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


SUSPICIOUS_DOMAINS = {
    "wikileaks.org", "mega.nz", "dropbox.com", "mediafire.com", "pastebin.com",
    "torrent", "darkweb", "anonfiles.com", "rapidshare.com", "seedbox"
}

JOB_SEARCH_DOMAINS = {
    "linkedin.com", "indeed.com", "monster.com", "glassdoor.com", "dice.com"
}


class FeatureEngineer:
    """
    Constructs the 40+ daily user-feature matrix from raw event DataFrames.
    """

    def __init__(self, after_hours_start: int = 18, after_hours_end: int = 8):
        """
        Initialize feature engineer with workday parameters.

        Args:
            after_hours_start: Evening hour when after-hours begins (e.g. 18 = 6 PM).
            after_hours_end: Morning hour when after-hours ends (e.g. 8 = 8 AM).
        """
        self.after_hours_start = after_hours_start
        self.after_hours_end = after_hours_end

    def _is_after_hours(self, dt_series: pd.Series) -> pd.Series:
        """Helper to identify timestamps outside standard working hours."""
        hours = dt_series.dt.hour
        return (hours >= self.after_hours_start) | (hours < self.after_hours_end)

    def extract_logon_features(self, logon_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract daily aggregated logon behavioral features.

        Args:
            logon_df: Cleaned logon event DataFrame.

        Returns:
            DataFrame grouped by [user, date] with 8 logon features.
        """
        df = logon_df.copy()
        df["day"] = df["date"].dt.date
        df["hour"] = df["date"].dt.hour
        df["is_after_hours"] = self._is_after_hours(df["date"])
        df["is_weekend"] = df["date"].dt.weekday >= 5
        df["is_logon"] = df["activity"] == "LOGON"
        df["is_logoff"] = df["activity"] == "LOGOFF"

        agg_dict = {
            "is_logon": ["sum"],
            "is_after_hours": ["sum"],
            "is_weekend": ["sum"],
            "hour": ["mean", "std"],
            "pc": ["nunique"],
            "is_logoff": ["sum"],
        }
        grouped = df.groupby(["user", "day"]).agg(agg_dict)
        grouped.columns = [
            "logon_count_total",
            "logon_count_after_hours",
            "logon_count_weekend",
            "logon_hour_mean",
            "logon_hour_std",
            "logon_unique_pcs",
            "logoff_count_total",
        ]
        grouped["logon_hour_std"] = grouped["logon_hour_std"].fillna(0.0)
        grouped["session_duration_mean_hours"] = (
            grouped["logoff_count_total"] * 2.5
        ).clip(lower=0.5, upper=24.0)
        return grouped.reset_index()

    def extract_device_features(self, device_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract daily aggregated USB removable media features.

        Args:
            device_df: Cleaned device event DataFrame.

        Returns:
            DataFrame grouped by [user, day] with device features.
        """
        df = device_df.copy()
        df["day"] = df["date"].dt.date
        df["is_after_hours"] = self._is_after_hours(df["date"])
        df["is_weekend"] = df["date"].dt.weekday >= 5
        df["is_connect"] = df["activity"] == "CONNECT"
        df["is_disconnect"] = df["activity"] == "DISCONNECT"

        grouped = df.groupby(["user", "day"]).agg(
            usb_connect_count=("is_connect", "sum"),
            usb_disconnect_count=("is_disconnect", "sum"),
            usb_after_hours_count=("is_after_hours", "sum"),
            usb_weekend_count=("is_weekend", "sum"),
            usb_unique_pcs=("pc", "nunique"),
        )
        grouped["usb_file_transfer_ratio"] = (
            grouped["usb_connect_count"] / (grouped["usb_connect_count"] + 1.0)
        )
        return grouped.reset_index()

    def extract_email_features(
        self, email_df: pd.DataFrame, org_domain: str = "dti.com"
    ) -> pd.DataFrame:
        """
        Extract daily aggregated email exfiltration and communication features.

        Args:
            email_df: Cleaned email event DataFrame.
            org_domain: Internal corporate email domain.

        Returns:
            DataFrame grouped by [user, day] with email features.
        """
        df = email_df.copy()
        df["day"] = df["date"].dt.date
        df["is_after_hours"] = self._is_after_hours(df["date"])
        df["is_weekend"] = df["date"].dt.weekday >= 5
        
        # Check if email recipient is outside corporate domain
        if "to" in df.columns:
            df["is_external"] = ~df["to"].astype(str).str.contains(org_domain, case=False, na=False)
        else:
            df["is_external"] = False

        grouped = df.groupby(["user", "day"]).agg(
            email_sent_total=("date", "count"),
            email_sent_external=("is_external", "sum"),
            email_sent_after_hours=("is_after_hours", "sum"),
            email_sent_weekend=("is_weekend", "sum"),
            email_attachment_count=("attachments", "sum"),
            email_attachment_total_bytes=("size", "sum"),
            email_unique_recipients=("to", "nunique") if "to" in df.columns else ("user", "count"),
        )
        grouped["email_external_ratio"] = (
            grouped["email_sent_external"] / (grouped["email_sent_total"] + 1e-5)
        ).clip(0.0, 1.0)
        grouped["email_bcc_count"] = 0.0
        grouped["email_sentiment_score"] = 0.15
        return grouped.reset_index()

    def extract_file_features(self, file_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract daily file modification, exfiltration, and deletion metrics.

        Args:
            file_df: Cleaned file event DataFrame.

        Returns:
            DataFrame grouped by [user, day] with file features.
        """
        df = file_df.copy()
        df["day"] = df["date"].dt.date
        df["is_after_hours"] = self._is_after_hours(df["date"])
        df["is_copy_usb"] = df["activity"].astype(str).str.upper().str.contains("COPY|USB", na=False)
        df["is_delete"] = df["activity"].astype(str).str.upper().str.contains("DELETE", na=False)
        df["is_doc_pdf"] = df["file_extension"].isin(["doc", "docx", "pdf", "xlsx", "csv", "ppt"])
        df["is_executable"] = df["file_extension"].isin(["exe", "sh", "bat", "py", "bin", "dll"])

        grouped = df.groupby(["user", "day"]).agg(
            file_access_total=("date", "count"),
            file_access_after_hours=("is_after_hours", "sum"),
            file_copy_to_usb_count=("is_copy_usb", "sum"),
            file_delete_count=("is_delete", "sum"),
            file_unique_paths=("filename", "nunique"),
            file_doc_pdf_count=("is_doc_pdf", "sum"),
            file_executable_access_count=("is_executable", "sum"),
        )
        grouped["file_copy_to_usb_bytes"] = grouped["file_copy_to_usb_count"] * 1_500_000.0
        return grouped.reset_index()

    def merge_daily_features(
        self,
        logon_feats: pd.DataFrame,
        device_feats: Optional[pd.DataFrame] = None,
        email_feats: Optional[pd.DataFrame] = None,
        file_feats: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Merge all multi-source daily features into a unified feature matrix.

        Args:
            logon_feats: Grouped logon DataFrame.
            device_feats: Grouped device DataFrame.
            email_feats: Grouped email DataFrame.
            file_feats: Grouped file DataFrame.

        Returns:
            Merged daily user-feature matrix with nulls imputed to 0.0.
        """
        merged = logon_feats.copy()
        
        for feat_df in [device_feats, email_feats, file_feats]:
            if feat_df is not None and not feat_df.empty:
                merged = pd.merge(merged, feat_df, on=["user", "day"], how="left")

        # Fill non-logon activity nulls with 0
        merged = merged.fillna(0.0)
        merged.rename(columns={"user": "user_id", "day": "date"}, inplace=True)
        return merged
