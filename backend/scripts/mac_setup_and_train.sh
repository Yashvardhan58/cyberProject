#!/usr/bin/env bash
# ==============================================================================
# AI-Powered Adaptive UEBA - MacBook Full Training & Deployment Automation Script
# Project: M.Tech Thesis (CMU CERT r5.2 Dataset)
# ==============================================================================

set -e

echo "=================================================================="
echo " Starting Full UEBA Ingestion, Training & Docker Pipeline (macOS) "
echo "=================================================================="

# 1. Environment Check
ARCH=$(uname -m)
echo "[+] Detected Architecture: $ARCH (Apple Silicon / Intel compatible)"

# Ensure Python 3.10+ is available
if ! command -v python3 &> /dev/null; then
    echo "[-] Error: python3 not found. Please install Python 3.10+ using brew: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "[+] Using $PYTHON_VERSION"

# 2. Virtual Environment Setup
VENV_DIR="venv_mac_train"
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating dedicated virtual environment: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

echo "[+] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Install Heavy ML & Ingestion Dependencies
echo "[+] Installing ML, XGBoost, SHAP, and Data Engineering dependencies..."
pip install --upgrade pip setuptools wheel
pip install numpy pandas scikit-learn xgboost imbalanced-learn shap joblib django djangorestframework django-cors-headers celery redis anthropic

# 4. CERT r5.2 Full Dataset Ingestion & Feature Engineering
CERT_DATA_DIR="${CERT_DATA_DIR:-./ml/data/raw/cert_r5.2}"
PROCESSED_DATA_DIR="./ml/data/processed"
MODELS_DIR="./ml/models/saved"

mkdir -p "$PROCESSED_DATA_DIR"
mkdir -p "$MODELS_DIR"

if [ -d "$CERT_DATA_DIR" ]; then
    echo "[+] Found CERT r5.2 dataset at: $CERT_DATA_DIR"
    echo "[+] Running chunked ingestion & feature engineering pipeline across 6 logs..."
    python3 ml/data/cert_ingestor.py --raw-dir "$CERT_DATA_DIR" --out-dir "$PROCESSED_DATA_DIR"
else
    echo "[!] Notice: CERT r5.2 directory ($CERT_DATA_DIR) not found."
    echo "[+] Falling back to high-fidelity synthetic feature vector generation..."
    python3 ml/data/synthetic_generator.py --count 5000 --out "$PROCESSED_DATA_DIR/full_feature_vectors.csv"
fi

# 5. Train All Models & Serialize Artifacts
echo "[+] Training SVM, XGBoost+SMOTE, Isolation Forest & TreeSHAP Explainer..."
python3 ml/models/train_all.py \
    --data "$PROCESSED_DATA_DIR/sample_vectors.csv" \
    --models-dir "$MODELS_DIR" \
    --governance-window 7

# 6. Execute Thesis Research Experiments (E1 through E5)
echo "=================================================================="
echo " Executing M.Tech Thesis Validation Experiments (E1 - E5)        "
echo "=================================================================="
python3 ml/experiments/e1_model_comparison.py
python3 ml/experiments/e2_poisoning_simulation.py
python3 ml/experiments/e3_governance_validation.py
python3 ml/experiments/e4_drift_classification.py
python3 ml/experiments/e5_faithfulness_eval.py

# 7. Seed Database
echo "[+] Populating SQLite / PostgreSQL database fixtures..."
python3 manage.py makemigrations
python3 manage.py migrate
python3 ml/data/seed_sqlite_db.py

echo "=================================================================="
echo " Full Training & Validation Completed Successfully!              "
echo " Saved Models in: backend/ml/models/saved/                       "
echo "=================================================================="
echo "To run full containerized stack:"
echo "  docker compose up --build"
echo "=================================================================="
