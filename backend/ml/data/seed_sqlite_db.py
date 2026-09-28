"""
Standalone SQLite Database Seeder for Adaptive UEBA.

Parses sample_vectors.csv and seeds rich, realistic relational data into SQLite
(users, peer groups, risk scores, alerts, SHAP values, baselines, governance logs,
explanations, verdicts, and experiment results) using Python standard library.
"""

import csv
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


DB_PATH = Path(__file__).resolve().parent.parent.parent / "db.sqlite3"
PROCESSED_DATA_PATH = Path(__file__).resolve().parent / "processed" / "sample_vectors.csv"


def create_sqlite_schema(conn: sqlite3.Connection) -> None:
    """Create all relational tables matching Django model schemas."""
    cursor = conn.cursor()

    # 1. Peer Groups
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users_peergroup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role VARCHAR(100) NOT NULL,
        department VARCHAR(100) NOT NULL,
        centroid_vector TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        UNIQUE (role, department)
    );
    """)

    # 2. User Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users_userprofile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(150) NOT NULL,
        email VARCHAR(254) UNIQUE NOT NULL,
        role VARCHAR(100) NOT NULL,
        department VARCHAR(100) NOT NULL,
        current_risk_score REAL NOT NULL,
        current_severity VARCHAR(20) NOT NULL,
        is_active BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        peer_group_id INTEGER,
        FOREIGN KEY (peer_group_id) REFERENCES users_peergroup (id)
    );
    """)

    # 3. Risk Scores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts_riskscore (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        xgb_score REAL NOT NULL,
        if_score REAL NOT NULL,
        peer_score REAL NOT NULL,
        user_score REAL NOT NULL,
        drift_score REAL NOT NULL,
        final_risk REAL NOT NULL,
        severity VARCHAR(20) NOT NULL,
        component_breakdown TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users_userprofile (id),
        UNIQUE (user_id, date)
    );
    """)

    # 4. Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts_alert (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        severity VARCHAR(20) NOT NULL,
        status VARCHAR(20) NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        top_feature_summary VARCHAR(255) NOT NULL,
        is_true_positive BOOLEAN,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        risk_score_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (risk_score_id) REFERENCES alerts_riskscore (id),
        FOREIGN KEY (user_id) REFERENCES users_userprofile (id)
    );
    """)

    # 5. SHAP Values
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts_shapvalue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature_name VARCHAR(150) NOT NULL,
        shap_value REAL NOT NULL,
        actual_value REAL NOT NULL,
        direction VARCHAR(10) NOT NULL,
        rank INTEGER NOT NULL,
        alert_id INTEGER NOT NULL,
        FOREIGN KEY (alert_id) REFERENCES alerts_alert (id),
        UNIQUE (alert_id, rank)
    );
    """)

    # 6. User Baselines
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS baselines_userbaseline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        baseline_date DATE NOT NULL,
        feature_vector TEXT NOT NULL,
        is_suppressed BOOLEAN NOT NULL,
        suppression_reason VARCHAR(255) NOT NULL,
        created_at DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users_userprofile (id),
        UNIQUE (user_id, baseline_date)
    );
    """)

    # 7. Governance Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS baselines_governancelog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_date DATE NOT NULL,
        stage_1_drift_rate_score REAL NOT NULL,
        stage_2_peer_divergence_score REAL NOT NULL,
        stage_3_monotonic_trend_score REAL NOT NULL,
        suspicion_score REAL NOT NULL,
        verdict VARCHAR(20) NOT NULL,
        reason VARCHAR(255) NOT NULL,
        action_taken VARCHAR(100) NOT NULL,
        created_at DATETIME NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users_userprofile (id)
    );
    """)

    # 8. Explanations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS explanations_explanation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evidence_object TEXT NOT NULL,
        explanation_text TEXT NOT NULL,
        faithfulness_score REAL NOT NULL,
        model_name VARCHAR(100) NOT NULL,
        created_at DATETIME NOT NULL,
        alert_id INTEGER UNIQUE NOT NULL,
        FOREIGN KEY (alert_id) REFERENCES alerts_alert (id)
    );
    """)

    # 9. Chat Sessions & Messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS explanations_chatsession (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analyst_name VARCHAR(150) NOT NULL,
        session_token VARCHAR(100) UNIQUE NOT NULL,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        alert_id INTEGER NOT NULL,
        FOREIGN KEY (alert_id) REFERENCES alerts_alert (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS explanations_chatmessage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role VARCHAR(20) NOT NULL,
        content TEXT NOT NULL,
        evidence_grounded BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        session_id INTEGER NOT NULL,
        FOREIGN KEY (session_id) REFERENCES explanations_chatsession (id)
    );
    """)

    # 10. Analyst Verdicts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verdicts_analystverdict (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        verdict VARCHAR(20) NOT NULL,
        analyst_name VARCHAR(150) NOT NULL,
        analyst_note TEXT NOT NULL,
        submitted_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        alert_id INTEGER UNIQUE NOT NULL,
        FOREIGN KEY (alert_id) REFERENCES alerts_alert (id)
    );
    """)

    # 11. Experiment Results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS metrics_experimentresult (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_name VARCHAR(10) UNIQUE NOT NULL,
        title VARCHAR(255) NOT NULL,
        research_question VARCHAR(255) NOT NULL,
        result_data TEXT NOT NULL,
        summary TEXT NOT NULL,
        run_at DATETIME NOT NULL
    );
    """)

    conn.commit()


def seed_database(db_path: Path = None, data_path: Path = None) -> Dict[str, int]:
    """Populate database from sample_vectors.csv and predefined experiment results."""
    target_db = db_path or DB_PATH
    target_data = data_path or PROCESSED_DATA_PATH

    print("=" * 60)
    print("SEEDING ADAPTIVE UEBA DATABASE...")
    print(f"Target SQLite Database: {target_db}")
    print("=" * 60)

    target_db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    create_sqlite_schema(conn)

    # Clean existing rows for fresh seed
    for tbl in [
        "verdicts_analystverdict", "explanations_chatmessage", "explanations_chatsession",
        "explanations_explanation", "alerts_shapvalue", "alerts_alert", "alerts_riskscore",
        "baselines_governancelog", "baselines_userbaseline", "users_userprofile",
        "users_peergroup", "metrics_experimentresult"
    ]:
        cursor.execute(f"DELETE FROM {tbl};")

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 1. Seed Peer Groups
    roles_dept = [
        ("Software Engineer", "Engineering"),
        ("Systems Administrator", "IT Operations"),
        ("Financial Analyst", "Finance"),
        ("HR Coordinator", "Human Resources"),
        ("Sales Executive", "Sales"),
    ]
    peer_group_ids = {}
    for role, dept in roles_dept:
        cursor.execute("""
        INSERT INTO users_peergroup (role, department, centroid_vector, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?);
        """, (role, dept, json.dumps({"baseline_logon": 2.5, "baseline_usb": 0.1, "baseline_email": 15.0}), now_iso, now_iso))
        peer_group_ids[(role, dept)] = cursor.lastrowid

    # 2. Seed Users
    user_names = {
        "USR0001": ("Sarah Jenkins", "sarah.jenkins@dti.com", "Software Engineer", "Engineering"),
        "USR0002": ("Marcus Vance", "marcus.vance@dti.com", "Systems Administrator", "IT Operations"),
        "USR0003": ("Elena Rostova", "elena.rostova@dti.com", "Financial Analyst", "Finance"),
        "USR0004": ("David Kim", "david.kim@dti.com", "HR Coordinator", "Human Resources"),
        "USR0005": ("Rachel Chen", "rachel.chen@dti.com", "Sales Executive", "Sales"),
        "USR0006": ("Alex Turner", "alex.turner@dti.com", "Software Engineer", "Engineering"),
        "USR0007": ("James Mitchell", "james.mitchell@dti.com", "Systems Administrator", "IT Operations"),
        "USR0008": ("Priya Sharma", "priya.sharma@dti.com", "Financial Analyst", "Finance"),
        "USR0009": ("Thomas Wright", "thomas.wright@dti.com", "HR Coordinator", "Human Resources"),
        "USR0010": ("Jessica Miller", "jessica.miller@dti.com", "Sales Executive", "Sales"),
    }

    user_db_ids = {}
    for emp_id, (name, email, role, dept) in user_names.items():
        pg_id = peer_group_ids.get((role, dept))
        cursor.execute("""
        INSERT INTO users_userprofile (employee_id, name, email, role, department, current_risk_score, current_severity, is_active, created_at, updated_at, peer_group_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (emp_id, name, email, role, dept, 25.0, "LOW", 1, now_iso, now_iso, pg_id))
        user_db_ids[emp_id] = cursor.lastrowid

    # 3. Ingest processed data to populate RiskScores and Alerts
    records = []
    if target_data.exists():
        with open(target_data, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)

    alert_count = 0
    risk_score_count = 0
    shap_count = 0
    max_user_scores = {uid: 0.0 for uid in user_db_ids}

    threat_scenarios = [
        ("Mass Removable Media File Staging", "file_copy_to_usb_bytes", "Transferred 142 files (450 MB) to unapproved USB drive outside business hours."),
        ("Abnormal Off-Hours Remote Access Spike", "logon_count_after_hours", "6 consecutive authentications between 01:00 AM and 04:00 AM from anomalous IP range."),
        ("High-Volume External Email Exfiltration", "email_external_ratio", "Dispatched 34.8 MB password-protected ZIP archive to external webmail address."),
        ("Unclassified Cloud Storage POST Activity", "http_suspicious_domain_count", "18 direct HTTP POST requests to mega-upload-cloud.net with payload size 125 MB."),
        ("Multi-Factor Authentication Bypass Pattern", "logon_failed_attempts", "Multiple rapid logon attempts followed by anomalous privilege elevation."),
        ("Source Code Repository Bulk Clone", "git_clone_volume", "Cloned 14 core repositories within a 15-minute window preceding weekend logout."),
        ("Internal Network Port Reconnaissance", "network_scan_ports", "Scanned 1,024 internal subnet endpoints across TCP ports 445 (SMB) and 3389 (RDP)."),
        ("Bulk Customer PII Database Dump", "db_query_row_count", "Exported 48,000 rows from production customers table to local temporary staging path."),
        ("Elevated Admin Privilege Group Modification", "user_group_privilege_change", "Added secondary account to domain Administrators group without active change ticket."),
    ]

    for idx, row in enumerate(records):
        emp_id = row["user_id"]
        user_pk = user_db_ids.get(emp_id)
        if not user_pk:
            continue

        record_date = row["date"]
        is_insider = int(row.get("is_insider", 0))

        # Diverse score distribution
        if is_insider:
            p_xgb = 0.88 + (idx % 10) * 0.01
            s_if = 0.82 + (idx % 8) * 0.01
            final_risk = round(85.0 + (idx % 14) * 0.9, 1)
            severity = "CRITICAL"
        elif idx % 3 == 0:
            p_xgb = 0.65
            s_if = 0.62
            final_risk = round(65.0 + (idx % 10) * 1.2, 1)
            severity = "HIGH"
        elif idx % 3 == 1:
            p_xgb = 0.45
            s_if = 0.40
            final_risk = round(42.0 + (idx % 12) * 1.1, 1)
            severity = "MEDIUM"
        else:
            p_xgb = 0.15
            s_if = 0.18
            final_risk = round(18.0 + (idx % 10) * 0.8, 1)
            severity = "LOW"

        d_peer = round(float(row.get("peer_deviation_score", 0.10)), 3)
        d_user = round(float(row.get("user_deviation_score", 0.08)), 3)
        d_drift = round(float(row.get("drift_suspicion_score", 0.05)), 3)

        max_user_scores[emp_id] = max(max_user_scores[emp_id], final_risk)

        breakdown = json.dumps({
            "p_xgb_contribution": round(0.35 * p_xgb * 100, 2),
            "s_if_contribution": round(0.25 * s_if * 100, 2),
            "d_peer_contribution": round(0.20 * d_peer * 100, 2),
            "d_user_contribution": round(0.15 * d_user * 100, 2),
            "d_drift_contribution": round(0.05 * d_drift * 100, 2),
        })

        cursor.execute("""
        INSERT INTO alerts_riskscore (date, xgb_score, if_score, peer_score, user_score, drift_score, final_risk, severity, component_breakdown, created_at, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (record_date, p_xgb, s_if, d_peer, d_user, d_drift, final_risk, severity, breakdown, now_iso, user_pk))
        rs_id = cursor.lastrowid
        risk_score_count += 1

        # Create Alert for all CRITICAL, HIGH, and MEDIUM items
        if severity in ["CRITICAL", "HIGH", "MEDIUM"]:
            alert_count += 1
            status = "OPEN" if alert_count % 2 == 1 else "INVESTIGATING"
            scenario = threat_scenarios[(alert_count - 1) % len(threat_scenarios)]
            title = scenario[0]
            top_feat_name = scenario[1]
            desc = scenario[2]

            cursor.execute("""
            INSERT INTO alerts_alert (severity, status, title, description, top_feature_summary, is_true_positive, created_at, updated_at, risk_score_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (severity, status, title, desc, top_feat_name, None, now_iso, now_iso, rs_id, user_pk))
            alert_id = cursor.lastrowid

            # Seed Top-5 SHAP values for this alert
            shap_candidates = [
                (top_feat_name, 0.42, 142.0, "positive"),
                ("email_external_ratio", 0.28, 0.85, "positive"),
                ("logon_count_after_hours", 0.18, 6.0, "positive"),
                ("http_suspicious_domain_count", 0.14, 18.0, "positive"),
                ("logon_failed_attempts", -0.05, 0.0, "negative"),
            ]
            for rank, (fname, sval, aval, direction) in enumerate(shap_candidates, start=1):
                cursor.execute("""
                INSERT INTO alerts_shapvalue (feature_name, shap_value, actual_value, direction, rank, alert_id)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (fname, sval, aval, direction, rank, alert_id))
                shap_count += 1

            # Seed Claude LLM Explanation
            evidence_obj = json.dumps({
                "alert_id": alert_id,
                "user": user_names[emp_id][0],
                "score": final_risk,
                "top_features": [
                    {"feature": "file_copy_to_usb_bytes", "shap": 0.42, "value": "50 MB"},
                    {"feature": "email_external_ratio", "shap": 0.28, "value": "85%"},
                ],
                "7_day_trend": "Monotonic escalation over last 7 days"
            })
            explanation_text = (
                f"Alert for {user_names[emp_id][0]} triggered primarily due to abnormal file copy volume to removable USB media "
                f"(SHAP impact: +0.42) combined with a surge in external email transmission (SHAP: +0.28). "
                f"Activity occurred outside standard business hours, deviating significantly from the engineering peer baseline."
            )
            cursor.execute("""
            INSERT INTO explanations_explanation (evidence_object, explanation_text, faithfulness_score, model_name, created_at, alert_id)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (evidence_obj, explanation_text, 0.96, "claude-3-5-sonnet-20241022", now_iso, alert_id))

            # Seed Chat Session & Message
            session_tok = f"sess_{alert_id}_{int(datetime.now(timezone.utc).timestamp())}"
            cursor.execute("""
            INSERT INTO explanations_chatsession (analyst_name, session_token, created_at, updated_at, alert_id)
            VALUES (?, ?, ?, ?, ?);
            """, ("Senior SOC Analyst", session_tok, now_iso, now_iso, alert_id))
            cs_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO explanations_chatmessage (role, content, evidence_grounded, created_at, session_id)
            VALUES (?, ?, ?, ?, ?);
            """, ("user", f"Why did the risk score spike to {final_risk}?", 1, now_iso, cs_id))
            cursor.execute("""
            INSERT INTO explanations_chatmessage (role, content, evidence_grounded, created_at, session_id)
            VALUES (?, ?, ?, ?, ?);
            """, ("assistant", explanation_text, 1, now_iso, cs_id))

            # Seed a sample Verdict for the first 3 alerts
            if alert_count <= 3:
                v_type = "TP" if is_insider else "FP"
                v_note = "Confirmed unauthorized data staging to personal USB device." if is_insider else "Legitimate scheduled backup batch."
                cursor.execute("""
                INSERT INTO verdicts_analystverdict (verdict, analyst_name, analyst_note, submitted_at, updated_at, alert_id)
                VALUES (?, ?, ?, ?, ?, ?);
                """, (v_type, "Senior SOC Analyst", v_note, now_iso, now_iso, alert_id))

    # Update User Profiles with calculated current scores
    for emp_id, max_score in max_user_scores.items():
        if max_score >= 80.0:
            sev = "CRITICAL"
        elif max_score >= 60.0:
            sev = "HIGH"
        elif max_score >= 30.0:
            sev = "MEDIUM"
        else:
            sev = "LOW"
        cursor.execute("""
        UPDATE users_userprofile SET current_risk_score = ?, current_severity = ? WHERE employee_id = ?;
        """, (max_score, sev, emp_id))

    # 4. Seed Baseline Governance Logs
    for emp_id, user_pk in user_db_ids.items():
        # Clean users allowed
        cursor.execute("""
        INSERT INTO baselines_governancelog (check_date, stage_1_drift_rate_score, stage_2_peer_divergence_score, stage_3_monotonic_trend_score, suspicion_score, verdict, reason, action_taken, created_at, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, ("2026-01-20", 0.12, 0.08, 0.15, 0.11, "ALLOW", "Normal operational drift within peer tolerance", "BASELINE_UPDATED", now_iso, user_pk))

    # Add 2 Suppressed poisoning attacks
    suspect_pk = user_db_ids["USR0001"]
    cursor.execute("""
    INSERT INTO baselines_governancelog (check_date, stage_1_drift_rate_score, stage_2_peer_divergence_score, stage_3_monotonic_trend_score, suspicion_score, verdict, reason, action_taken, created_at, user_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, ("2026-01-25", 0.72, 0.81, 0.88, 0.80, "SUPPRESS", "Unilateral peer divergence and persistent 7-day escalation", "BASELINE_FROZEN", now_iso, suspect_pk))

    # 5. Seed Experiment Results (E1 to E5)
    exp_data = [
        ("E1", "Model Comparison (SVM vs XGBoost vs Hybrid)", "Which model combination achieves optimal detection?",
         {"SVM": {"auc": 0.8842, "f1": 0.7879}, "XGBoost": {"auc": 0.9415, "f1": 0.8885}, "Hybrid": {"auc": 0.9782, "f1": 0.9412}},
         "Hybrid Adaptive Fusion achieves highest AUC (0.9782) and F1-Score (0.9412)."),
        ("E2", "Slow-Escalation Poisoning Without Governance", "Does baseline become contaminated under 5%/month escalation?",
         {"months": ["M1", "M2", "M3", "M4", "M5", "M6"], "detection_rate": [0.94, 0.88, 0.74, 0.58, 0.41, 0.22]},
         "Without governance, detection rate plummets from 94% to 22% by Month 6."),
        ("E3", "Poisoning Defense Validation With Governance", "Does governance engine prevent contamination?",
         {"months": ["M1", "M2", "M3", "M4", "M5", "M6"], "governed_rate": [0.94, 0.93, 0.92, 0.94, 0.91, 0.93]},
         "Governance Engine maintains ~93% detection rate throughout 6-month slow escalation attack."),
        ("E4", "Legitimate Role-Change vs Malicious Drift", "Can system distinguish legitimate role changes from attacks?",
         {"accuracy": 0.9400, "precision": 0.9583, "recall": 0.9200, "false_suppression": 0.04},
         "Peer-anchor divergence separates legitimate role changes with 94.0% accuracy."),
        ("E5", "FaithLens LLM Explanation Faithfulness", "Can Claude generate faithful evidence-grounded explanations?",
         {"factuality": 0.9717, "directional_consistency": 0.9767, "completeness": 0.9000, "overall_faithfulness": 0.9555},
         "Overall explanation faithfulness reaches 0.9555, exceeding the 0.85 academic benchmark."),
    ]

    for name, title, rq, data, summary in exp_data:
        cursor.execute("""
        INSERT INTO metrics_experimentresult (experiment_name, title, research_question, result_data, summary, run_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (name, title, rq, json.dumps(data), summary, now_iso))

    conn.commit()
    conn.close()

    counts = {
        "users": len(user_db_ids),
        "peer_groups": len(peer_group_ids),
        "risk_scores": risk_score_count,
        "alerts": alert_count,
        "shap_values": shap_count,
        "experiments": len(exp_data),
    }

    print("\nDATABASE SEEDED SUCCESSFULLY:")
    for k, v in counts.items():
        print(f"  • {k.replace('_', ' ').title()}: {v}")
    print("=" * 60)
    return counts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Seed SQLite database for Adaptive UEBA")
    parser.add_argument("--data", type=str, default=None, help="Path to custom processed CSV vectors")
    parser.add_argument("--db", type=str, default=None, help="Path to custom sqlite database")
    args = parser.parse_args()

    custom_db = Path(args.db) if args.db else None
    custom_data = Path(args.data) if args.data else None
    seed_database(db_path=custom_db, data_path=custom_data)
