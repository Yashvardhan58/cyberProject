"""
Unified Model Training and Pipeline Execution Script.

Loads processed daily vectors, trains SVM, XGBoost+SMOTE, and Isolation Forest,
evaluates test performance, and serializes all models to disk.
Executable via: `python backend/ml/models/train_all.py`
"""

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add backend and project root to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
repo_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(repo_root))

from ml.models.svm_model import SVMThreatClassifier
from ml.models.xgboost_model import XGBoostThreatClassifier
from ml.models.isolation_forest import IsolationForestAnomalyScorer
from ml.models.shap_explainer import SHAPThreatExplainer
from ml.models.risk_fusion import RiskFusionEngine
from ml.baseline.baseline_engine import BaselineEngine
from ml.baseline.governance import BaselineGovernanceEngine


METADATA_COLS = {"user_id", "date", "role", "department", "is_insider"}


def load_csv_data(filepath: Path) -> Tuple[List[Dict], List[str]]:
    """Load CSV records using standard library."""
    records = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            records.append(row)
    feature_cols = [c for c in fieldnames if c not in METADATA_COLS]
    return records, feature_cols


def run_training_pipeline() -> Dict[str, Any]:
    """Execute end-to-end model training, evaluation, and serialization."""
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / "data" / "processed"
    saved_models_dir = base_dir / "models" / "saved"
    saved_models_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("STARTING ADAPTIVE UEBA MODEL TRAINING PIPELINE")
    print("=" * 65)

    # 1. Load Data
    train_path = processed_dir / "sample_vectors_train.csv"
    test_path = processed_dir / "sample_vectors_test.csv"
    
    train_records, feature_cols = load_csv_data(train_path)
    test_records, _ = load_csv_data(test_path)
    
    print(f"Data Loaded: {len(train_records)} train samples, {len(test_records)} test samples, {len(feature_cols)} features.")

    X_train = [[float(r[col]) for col in feature_cols] for r in train_records]
    y_train = [int(r["is_insider"]) for r in train_records]
    X_test = [[float(r[col]) for col in feature_cols] for r in test_records]
    y_test = [int(r["is_insider"]) for r in test_records]

    # 2. Train SVM Baseline
    print("\n[1/4] Training SVM Baseline Classifier...")
    svm = SVMThreatClassifier(C=1.0, random_state=42)
    svm_info = svm.train(X_train, y_train)
    svm.save(saved_models_dir / "svm_model.joblib")
    svm_preds = svm.predict_proba(X_test)
    print("  SVM trained successfully.")

    # 3. Train XGBoost + SMOTE
    print("\n[2/4] Training XGBoost Classifier with SMOTE...")
    xgb = XGBoostThreatClassifier(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
    xgb_info = xgb.train(X_train, y_train, feature_names=feature_cols, apply_smote=True)
    xgb.save(saved_models_dir / "xgboost_model.joblib")
    xgb_preds = xgb.predict_proba(X_test)
    print("  XGBoost trained successfully.")

    # 4. Train Isolation Forest
    print("\n[3/4] Training Isolation Forest Anomaly Scorer...")
    iforest = IsolationForestAnomalyScorer(n_estimators=100, contamination=0.08, random_state=42)
    if_info = iforest.train(X_train)
    iforest.save(saved_models_dir / "isolation_forest.joblib")
    if_preds = iforest.score_samples(X_test)
    print("  Isolation Forest trained successfully.")

    # 5. Baseline Engine & Governance Check
    print("\n[4/4] Fitting Baseline Engine & Peer Centroids...")
    baseline_eng = BaselineEngine(rolling_window_days=30)
    for row in train_records:
        vec = [float(row[c]) for c in feature_cols]
        baseline_eng.update_user_history(row["user_id"], vec)
    
    governance = BaselineGovernanceEngine(suspicion_threshold=0.60)
    print("  Baseline Engine fitted.")

    # 6. SHAP Explainer
    explainer = SHAPThreatExplainer(model=xgb.model, feature_names=feature_cols)
    sample_shap = explainer.explain_instance(X_test[0], top_k=5)

    # 7. Compute Risk Scores for Test Set
    risk_results = []
    for i, test_row in enumerate(test_records):
        p_x = float(xgb_preds[i])
        s_i = float(if_preds[i])
        vec = X_test[i]
        d_p = baseline_eng.calculate_peer_deviation(
            test_row.get("role", "Software Engineer"),
            test_row.get("department", "Engineering"),
            vec
        )
        d_u = baseline_eng.calculate_user_deviation(test_row["user_id"], vec)
        
        score, severity, breakdown = RiskFusionEngine.calculate_risk_score(
            p_xgb=p_x, s_if=s_i, d_peer=d_p, d_user=d_u
        )
        risk_results.append({"user_id": test_row["user_id"], "score": score, "severity": severity})

    mean_score = sum(r["score"] for r in risk_results) / len(risk_results)

    summary = {
        "status": "success",
        "train_samples": len(train_records),
        "test_samples": len(test_records),
        "feature_count": len(feature_cols),
        "sample_top_shap": sample_shap,
        "mean_test_risk_score": round(mean_score, 2),
        "test_severity_distribution": {
            "CRITICAL": sum(1 for r in risk_results if r["severity"] == "CRITICAL"),
            "HIGH": sum(1 for r in risk_results if r["severity"] == "HIGH"),
            "MEDIUM": sum(1 for r in risk_results if r["severity"] == "MEDIUM"),
            "LOW": sum(1 for r in risk_results if r["severity"] == "LOW"),
        }
    }

    with open(saved_models_dir / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 65)
    print("ALL MODELS TRAINED & SAVED SUCCESSFULLY TO:")
    print(f"  {saved_models_dir}")
    print(f"  Mean Risk Score: {summary['mean_test_risk_score']}")
    print(f"  Severities: {summary['test_severity_distribution']}")
    print("=" * 65)
    return summary


if __name__ == "__main__":
    run_training_pipeline()
