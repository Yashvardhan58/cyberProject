"""
Synthetic Dataset Generator for Local Development.

Generates realistic, lightweight CERT r5.2 compatible feature vectors and raw mock
logs to enable zero-disk-bloat local backend, API, and UI development (< 100 KB total).
Uses Python standard library (zero external dependencies required).
"""

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


FEATURE_COLUMNS = [
    # Logon Activity (8)
    "logon_count_total",
    "logon_count_after_hours",
    "logon_count_weekend",
    "logon_hour_mean",
    "logon_hour_std",
    "logon_unique_pcs",
    "logoff_count_total",
    "session_duration_mean_hours",
    
    # Device & USB Activity (6)
    "usb_connect_count",
    "usb_disconnect_count",
    "usb_after_hours_count",
    "usb_weekend_count",
    "usb_unique_pcs",
    "usb_file_transfer_ratio",
    
    # Email Activity (10)
    "email_sent_total",
    "email_sent_external",
    "email_external_ratio",
    "email_sent_after_hours",
    "email_sent_weekend",
    "email_attachment_count",
    "email_attachment_total_bytes",
    "email_unique_recipients",
    "email_bcc_count",
    "email_sentiment_score",
    
    # File & Removable Media Activity (8)
    "file_access_total",
    "file_access_after_hours",
    "file_copy_to_usb_count",
    "file_copy_to_usb_bytes",
    "file_delete_count",
    "file_unique_paths",
    "file_doc_pdf_count",
    "file_executable_access_count",
    
    # HTTP & Web Browsing Activity (8)
    "http_requests_total",
    "http_requests_after_hours",
    "http_requests_weekend",
    "http_suspicious_domain_count",
    "http_suspicious_domain_ratio",
    "http_upload_bytes_total",
    "http_download_bytes_total",
    "http_job_search_domain_count",
    
    # Baseline & Behavioral Drift (4)
    "peer_deviation_score",
    "user_deviation_score",
    "role_normalised_access_score",
    "drift_suspicion_score",
]

HEADER = ["user_id", "date", "role", "department", "is_insider"] + FEATURE_COLUMNS


def generate_synthetic_feature_records(
    n_records: int = 120,
    malicious_ratio: float = 0.10,
    random_seed: int = 42,
) -> List[Dict]:
    """
    Generate synthetic user-feature dictionaries matching CERT r5.2 structure.

    Args:
        n_records: Total number of user-day records to generate.
        malicious_ratio: Proportion of anomalous/insider threat days (0.0 to 1.0).
        random_seed: Seed for random generator reproducibility.

    Returns:
        List of dictionaries with user metadata and 44 continuous behavioral features.
    """
    random.seed(random_seed)

    user_pool = [f"USR{i:04d}" for i in range(1, 11)]
    roles = [
        "Software Engineer",
        "Systems Administrator",
        "Financial Analyst",
        "HR Coordinator",
        "Sales Executive",
    ]
    departments = ["Engineering", "IT Operations", "Finance", "Human Resources", "Sales"]
    role_dept_map = dict(zip(roles, departments))

    records: List[Dict] = []
    base_date = datetime(2026, 1, 1)

    for idx in range(n_records):
        user_id = user_pool[idx % len(user_pool)]
        user_role = roles[idx % len(roles)]
        department = role_dept_map[user_role]
        record_date = base_date + timedelta(days=idx // len(user_pool))

        # Check if record is anomalous/insider
        is_malicious = 1 if (random.random() < malicious_ratio) else 0

        if is_malicious == 0:
            # Benign baseline activity
            feat_dict = {
                "logon_count_total": random.randint(1, 4),
                "logon_count_after_hours": 1 if random.random() < 0.1 else 0,
                "logon_count_weekend": 1 if random.random() < 0.05 else 0,
                "logon_hour_mean": round(random.gauss(8.8, 0.5), 2),
                "logon_hour_std": round(abs(random.gauss(0.4, 0.1)), 2),
                "logon_unique_pcs": 1,
                "logoff_count_total": random.randint(1, 4),
                "session_duration_mean_hours": round(random.uniform(7.5, 9.0), 2),
                
                "usb_connect_count": 1 if random.random() < 0.15 else 0,
                "usb_disconnect_count": 1 if random.random() < 0.15 else 0,
                "usb_after_hours_count": 0,
                "usb_weekend_count": 0,
                "usb_unique_pcs": 1 if random.random() < 0.1 else 0,
                "usb_file_transfer_ratio": round(random.uniform(0.0, 0.05), 4),
                
                "email_sent_total": random.randint(5, 30),
                "email_sent_external": random.randint(0, 5),
                "email_external_ratio": round(random.uniform(0.0, 0.20), 4),
                "email_sent_after_hours": 1 if random.random() < 0.15 else 0,
                "email_sent_weekend": 0,
                "email_attachment_count": random.randint(0, 4),
                "email_attachment_total_bytes": random.randint(10_000, 150_000),
                "email_unique_recipients": random.randint(2, 10),
                "email_bcc_count": 0,
                "email_sentiment_score": round(random.uniform(0.1, 0.35), 2),
                
                "file_access_total": random.randint(10, 50),
                "file_access_after_hours": random.randint(0, 2),
                "file_copy_to_usb_count": 0,
                "file_copy_to_usb_bytes": 0,
                "file_delete_count": random.randint(0, 3),
                "file_unique_paths": random.randint(3, 15),
                "file_doc_pdf_count": random.randint(2, 10),
                "file_executable_access_count": 0,
                
                "http_requests_total": random.randint(80, 400),
                "http_requests_after_hours": random.randint(0, 5),
                "http_requests_weekend": 0,
                "http_suspicious_domain_count": 0,
                "http_suspicious_domain_ratio": 0.0,
                "http_upload_bytes_total": random.randint(20_000, 200_000),
                "http_download_bytes_total": random.randint(1_000_000, 8_000_000),
                "http_job_search_domain_count": 0,
                
                "peer_deviation_score": round(random.uniform(0.05, 0.35), 4),
                "user_deviation_score": round(random.uniform(0.02, 0.28), 4),
                "role_normalised_access_score": round(random.uniform(0.1, 0.40), 4),
                "drift_suspicion_score": round(random.uniform(0.01, 0.25), 4),
            }
        else:
            # Anomalous / Malicious Spike Pattern
            feat_dict = {
                "logon_count_total": random.randint(6, 15),
                "logon_count_after_hours": random.randint(3, 8),
                "logon_count_weekend": random.randint(1, 4),
                "logon_hour_mean": round(random.choice([2.5, 23.2, 4.1]), 2),
                "logon_hour_std": round(random.uniform(2.5, 4.5), 2),
                "logon_unique_pcs": random.randint(3, 7),
                "logoff_count_total": random.randint(6, 15),
                "session_duration_mean_hours": round(random.uniform(13.0, 18.0), 2),
                
                "usb_connect_count": random.randint(3, 10),
                "usb_disconnect_count": random.randint(3, 10),
                "usb_after_hours_count": random.randint(2, 6),
                "usb_weekend_count": random.randint(1, 4),
                "usb_unique_pcs": random.randint(2, 5),
                "usb_file_transfer_ratio": round(random.uniform(0.65, 0.95), 4),
                
                "email_sent_total": random.randint(40, 120),
                "email_sent_external": random.randint(30, 95),
                "email_external_ratio": round(random.uniform(0.70, 0.98), 4),
                "email_sent_after_hours": random.randint(15, 45),
                "email_sent_weekend": random.randint(5, 20),
                "email_attachment_count": random.randint(15, 40),
                "email_attachment_total_bytes": random.randint(5_000_000, 25_000_000),
                "email_unique_recipients": random.randint(25, 60),
                "email_bcc_count": random.randint(5, 18),
                "email_sentiment_score": round(random.uniform(-0.8, -0.4), 2),
                
                "file_access_total": random.randint(150, 600),
                "file_access_after_hours": random.randint(80, 350),
                "file_copy_to_usb_count": random.randint(20, 90),
                "file_copy_to_usb_bytes": random.randint(20_000_000, 150_000_000),
                "file_delete_count": random.randint(15, 60),
                "file_unique_paths": random.randint(50, 180),
                "file_doc_pdf_count": random.randint(40, 120),
                "file_executable_access_count": random.randint(2, 8),
                
                "http_requests_total": random.randint(800, 2500),
                "http_requests_after_hours": random.randint(300, 900),
                "http_requests_weekend": random.randint(100, 400),
                "http_suspicious_domain_count": random.randint(5, 25),
                "http_suspicious_domain_ratio": round(random.uniform(0.15, 0.45), 4),
                "http_upload_bytes_total": random.randint(10_000_000, 80_000_000),
                "http_download_bytes_total": random.randint(50_000_000, 300_000_000),
                "http_job_search_domain_count": random.randint(3, 12),
                
                "peer_deviation_score": round(random.uniform(0.75, 0.98), 4),
                "user_deviation_score": round(random.uniform(0.70, 0.96), 4),
                "role_normalised_access_score": round(random.uniform(0.78, 0.99), 4),
                "drift_suspicion_score": round(random.uniform(0.68, 0.94), 4),
            }

        row = {
            "user_id": user_id,
            "date": record_date.strftime("%Y-%m-%d"),
            "role": user_role,
            "department": department,
            "is_insider": is_malicious,
            **feat_dict,
        }
        records.append(row)

    return records


def write_csv(filepath: Path, records: List[Dict]) -> None:
    """Write list of records to CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(records)


def save_synthetic_dataset(output_dir: Path) -> Tuple[Path, Path, Path]:
    """
    Generate and save synthetic train and test fixtures.

    Args:
        output_dir: Target directory for processed vectors.

    Returns:
        Tuple of paths: (full_fixture_path, train_fixture_path, test_fixture_path)
    """
    records = generate_synthetic_feature_records(n_records=120, malicious_ratio=0.10, random_seed=42)

    # Chronological Split (80% train, 20% test)
    split_idx = int(len(records) * 0.8)
    train_records = records[:split_idx]
    test_records = records[split_idx:]

    full_path = output_dir / "sample_vectors.csv"
    train_path = output_dir / "sample_vectors_train.csv"
    test_path = output_dir / "sample_vectors_test.csv"

    write_csv(full_path, records)
    write_csv(train_path, train_records)
    write_csv(test_path, test_records)

    return full_path, train_path, test_path


if __name__ == "__main__":
    target_dir = Path(__file__).resolve().parent / "processed"
    full_p, train_p, test_p = save_synthetic_dataset(target_dir)
    print(f"Synthetic fixtures created successfully:")
    print(f"  Full:  {full_p}")
    print(f"  Train: {train_p}")
    print(f"  Test:  {test_p}")
