"""
CERT Insider Threat Dataset Ingestion Module.

Reads all 6 raw CSV files (logon, file, email, http, device, psychometric) from
the CERT r5.2 dataset with memory-efficient chunking, error handling, and type normalization.
"""

from pathlib import Path
from typing import Dict, Generator, Optional
import pandas as pd


CERT_FILES = {
    "logon": "logon.csv",
    "device": "device.csv",
    "email": "email.csv",
    "file": "file.csv",
    "http": "http.csv",
    "psychometric": "psychometric.csv",
}


class CertIngestor:
    """
    Ingestor class for Carnegie Mellon CERT Insider Threat Dataset r5.2.
    """

    def __init__(self, raw_data_dir: Path):
        """
        Initialize the CertIngestor with the raw dataset directory path.

        Args:
            raw_data_dir: Path to directory containing raw CERT CSV files.
        """
        self.raw_data_dir = Path(raw_data_dir)

    def verify_files_exist(self) -> Dict[str, bool]:
        """
        Check which CERT dataset files are present in the raw directory.

        Returns:
            Dictionary mapping log type to existence boolean.
        """
        status: Dict[str, bool] = {}
        for log_type, filename in CERT_FILES.items():
            file_path = self.raw_data_dir / filename
            status[log_type] = file_path.exists()
        return status

    def load_logon_logs(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load logon.csv containing user logon/logoff events and workstation IDs.

        Args:
            nrows: Optional row limit for sampling.

        Returns:
            pd.DataFrame with standardized columns [id, date, user, pc, activity].
        """
        file_path = self.raw_data_dir / CERT_FILES["logon"]
        if not file_path.exists():
            raise FileNotFoundError(f"Missing CERT file: {file_path}")

        df = pd.read_csv(
            file_path,
            nrows=nrows,
            parse_dates=["date"],
            dtype={"id": str, "user": str, "pc": str, "activity": str},
        )
        return df

    def load_device_logs(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load device.csv containing USB connect/disconnect events.

        Args:
            nrows: Optional row limit for sampling.

        Returns:
            pd.DataFrame with standardized columns [id, date, user, pc, activity].
        """
        file_path = self.raw_data_dir / CERT_FILES["device"]
        if not file_path.exists():
            raise FileNotFoundError(f"Missing CERT file: {file_path}")

        df = pd.read_csv(
            file_path,
            nrows=nrows,
            parse_dates=["date"],
            dtype={"id": str, "user": str, "pc": str, "activity": str},
        )
        return df

    def load_email_logs(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load email.csv containing email sender, recipients, attachments, and sizes.

        Args:
            nrows: Optional row limit for sampling.

        Returns:
            pd.DataFrame with email event data.
        """
        file_path = self.raw_data_dir / CERT_FILES["email"]
        if not file_path.exists():
            raise FileNotFoundError(f"Missing CERT file: {file_path}")

        df = pd.read_csv(
            file_path,
            nrows=nrows,
            parse_dates=["date"],
            dtype={"id": str, "user": str, "pc": str, "to": str, "from": str},
        )
        return df

    def load_file_logs(self, nrows: Optional[int] = None) -> pd.DataFrame:
        """
        Load file.csv containing file copy, open, and deletion events.

        Args:
            nrows: Optional row limit for sampling.

        Returns:
            pd.DataFrame with file event records.
        """
        file_path = self.raw_data_dir / CERT_FILES["file"]
        if not file_path.exists():
            raise FileNotFoundError(f"Missing CERT file: {file_path}")

        df = pd.read_csv(
            file_path,
            nrows=nrows,
            parse_dates=["date"],
            dtype={"id": str, "user": str, "pc": str, "filename": str, "activity": str},
        )
        return df

    def load_http_logs_chunked(
        self, chunksize: int = 100_000
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Stream large http.csv file in chunks to prevent memory exhaustion.

        Args:
            chunksize: Number of lines per chunk.

        Yields:
            pd.DataFrame chunk of HTTP browsing events.
        """
        file_path = self.raw_data_dir / CERT_FILES["http"]
        if not file_path.exists():
            raise FileNotFoundError(f"Missing CERT file: {file_path}")

        for chunk in pd.read_csv(
            file_path,
            chunksize=chunksize,
            parse_dates=["date"],
            dtype={"id": str, "user": str, "pc": str, "url": str},
        ):
            yield chunk

    def load_psychometric_scores(self) -> pd.DataFrame:
        """
        Load psychometric.csv containing Big Five personality scores and user attributes.

        Returns:
            pd.DataFrame with psychometric metrics per employee.
        """
        file_path = self.raw_data_dir / CERT_FILES["psychometric"]
        if not file_path.exists():
            raise FileNotFoundError(f"Missing CERT file: {file_path}")

        df = pd.read_csv(file_path, dtype={"user_id": str})
        return df


if __name__ == "__main__":
    import argparse
    import sys

    backend_root = Path(__file__).resolve().parent.parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    from ml.data.feature_engineer import run_batch_feature_pipeline

    parser = argparse.ArgumentParser(description="CERT r5.2 Ingestion & Feature Engineering")
    parser.add_argument("--raw-dir", type=str, default="./ml/data/raw", help="Path to raw CERT CSV directory")
    parser.add_argument("--out-dir", type=str, default="./ml/data/processed", help="Path to processed output directory")
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit for fast testing")
    args = parser.parse_args()

    target_raw = backend_root / args.raw_dir if not Path(args.raw_dir).is_absolute() else Path(args.raw_dir)
    target_out = backend_root / args.out_dir if not Path(args.out_dir).is_absolute() else Path(args.out_dir)

    run_batch_feature_pipeline(target_raw, target_out, sample_limit=args.limit)

