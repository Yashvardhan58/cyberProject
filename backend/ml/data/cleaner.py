"""
CERT Dataset Data Cleaning and Preprocessing Module.

Cleans null values, normalizes all timestamps to UTC, removes duplicate records,
and enforces data integrity across user IDs.
"""

from typing import List, Optional
import pandas as pd


class DataCleaner:
    """
    Standardizes and sanitizes raw CERT activity log DataFrames.
    """

    @staticmethod
    def clean_logon_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean logon logs: drop missing users/dates, normalize activities to uppercase.

        Args:
            df: Raw logon DataFrame.

        Returns:
            Sanitized logon DataFrame with UTC timestamps.
        """
        cleaned = df.dropna(subset=["date", "user", "activity"]).copy()
        cleaned["date"] = pd.to_datetime(cleaned["date"], utc=True)
        cleaned["activity"] = cleaned["activity"].str.strip().str.upper()
        cleaned["user"] = cleaned["user"].str.strip()
        cleaned["pc"] = cleaned["pc"].str.strip()
        cleaned = cleaned.drop_duplicates(subset=["date", "user", "pc", "activity"])
        return cleaned.sort_values(by="date").reset_index(drop=True)

    @staticmethod
    def clean_device_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean device (USB) logs: drop nulls, normalize activity (CONNECT/DISCONNECT).

        Args:
            df: Raw device DataFrame.

        Returns:
            Sanitized device DataFrame.
        """
        cleaned = df.dropna(subset=["date", "user", "activity"]).copy()
        cleaned["date"] = pd.to_datetime(cleaned["date"], utc=True)
        cleaned["activity"] = cleaned["activity"].str.strip().str.upper()
        cleaned["user"] = cleaned["user"].str.strip()
        cleaned["pc"] = cleaned["pc"].str.strip()
        cleaned = cleaned.drop_duplicates(subset=["date", "user", "pc", "activity"])
        return cleaned.sort_values(by="date").reset_index(drop=True)

    @staticmethod
    def clean_email_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean email logs: sanitize recipients, calculate attachment counts and sizes.

        Args:
            df: Raw email DataFrame.

        Returns:
            Sanitized email DataFrame.
        """
        cleaned = df.dropna(subset=["date", "user"]).copy()
        cleaned["date"] = pd.to_datetime(cleaned["date"], utc=True)
        cleaned["user"] = cleaned["user"].str.strip()
        
        # Fill missing attachment metadata with defaults
        if "attachments" in cleaned.columns:
            if cleaned["attachments"].dtype == object:
                cleaned["attachments"] = cleaned["attachments"].apply(
                    lambda x: len(str(x).split(";")) if pd.notna(x) and str(x).strip() and str(x) != "0" else 0
                ).astype(int)
            else:
                cleaned["attachments"] = pd.to_numeric(cleaned["attachments"], errors="coerce").fillna(0).astype(int)
        else:
            cleaned["attachments"] = 0
            
        if "size" in cleaned.columns:
            cleaned["size"] = pd.to_numeric(cleaned["size"], errors="coerce").fillna(0).astype(int)
        else:
            cleaned["size"] = 0
            
        cleaned = cleaned.drop_duplicates(subset=["date", "user", "to", "from"])
        return cleaned.sort_values(by="date").reset_index(drop=True)

    @staticmethod
    def clean_file_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean file activity logs: drop missing paths, parse extensions.

        Args:
            df: Raw file DataFrame.

        Returns:
            Sanitized file DataFrame.
        """
        cleaned = df.dropna(subset=["date", "user", "filename"]).copy()
        cleaned["date"] = pd.to_datetime(cleaned["date"], utc=True)
        cleaned["user"] = cleaned["user"].str.strip()
        cleaned["filename"] = cleaned["filename"].str.strip()
        cleaned["file_extension"] = (
            cleaned["filename"].str.split(".").str[-1].str.lower()
        )
        cleaned = cleaned.drop_duplicates(subset=["date", "user", "filename", "activity"])
        return cleaned.sort_values(by="date").reset_index(drop=True)

    @staticmethod
    def clean_http_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean HTTP browsing logs: extract host domain names and sanitize URLs.

        Args:
            df: Raw HTTP DataFrame chunk.

        Returns:
            Sanitized HTTP DataFrame.
        """
        cleaned = df.dropna(subset=["date", "user", "url"]).copy()
        cleaned["date"] = pd.to_datetime(cleaned["date"], utc=True)
        cleaned["user"] = cleaned["user"].str.strip()
        cleaned["url"] = cleaned["url"].str.strip()
        return cleaned.reset_index(drop=True)
