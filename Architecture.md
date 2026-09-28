# System Architecture
## AI-Powered Adaptive UEBA for Insider Threat Detection

---

## 1. High-Level Overview

The system is structured as five loosely-coupled components that communicate through well-defined interfaces:

  [CERT CSV Files]
       |
       v
  [Data Pipeline] --> [Feature Matrix] --> [ML Engine] --> [Risk Fusion]
                                                               |
                                             [Baseline Engine]--+
                                                               |
                                                         [Django REST API]
                                                               |
                                              +----------------+----------------+
                                              |                |                |
                                      [Celery Worker]   [PostgreSQL]      [Redis Cache]
                                              |
                                       [Claude API]
                                              |
                                       [React Dashboard]

---

## 2. Two-Environment Operational Architecture

To accommodate local storage constraints (e.g. < 4 GB available disk) while leveraging powerful external hardware (e.g. Client MacBook) for heavy dataset processing, the system is designed with a decoupled **Two-Environment Architecture**:

```
 ┌────────────────────────────────────────────────────────┐
 │ ENVIRONMENT 1: LOCAL LAPTOP (Development & UI Mode)   │
 │ • Footprint: < 200 MB disk space                       │
 │ • Database: SQLite (lightweight) / Local Django        │
 │ • Data: 50-row synthetic fixture (sample_vectors.csv)  │
 │ • Purpose: Code authoring, API tests, React Dashboard   │
 └───────────────────────────┬────────────────────────────┘
                             │ Git Push / Pull
                             ▼
 ┌────────────────────────────────────────────────────────┐
 │ ENVIRONMENT 2: MACBOOK HOST (Training & Demo Mode)     │
 │ • Dataset: Full CMU CERT r5.2 (15+ GB uncompressed)    │
 │ • Database: PostgreSQL 15 (Docker)                     │
 │ • Tasks: Full feature extraction & Model Training      │
 │ • Output: Serialized lightweight .joblib models & E1-E5│
 └────────────────────────────────────────────────────────┘
```

---

## 3. Layer Breakdown

### Layer 1: Data Layer
**Responsibility:** Ingest raw CERT logs, clean, and engineer features.

Components:
- `cert_ingestor.py`       -- reads all 6 CSV sources into pandas DataFrames with chunking
- `cleaner.py`             -- null handling, timestamp normalisation to UTC, deduplication
- `feature_engineer.py`    -- aggregates raw events into daily user-feature vectors (40+ features)
- `splitter.py`            -- enforces chronological train/test split (no random splitting)
- `synthetic_generator.py` -- generates lightweight sample fixtures for local UI/API testing

Output: `daily_vectors.csv` + PostgreSQL table `user_daily_features`

---

### Layer 2: Intelligence Layer
**Responsibility:** Score each user-day with risk, maintain contamination-resistant baselines.

Components:
- `svm_model.py`           -- SVM baseline classifier (scikit-learn)
- `xgboost_model.py`       -- XGBoost primary classifier + SMOTE oversampling
- `isolation_forest.py`    -- global anomaly scorer
- `shap_explainer.py`      -- post-hoc SHAP for XGBoost predictions (top-5 JSON output)
- `risk_fusion.py`         -- fuses all scores into 0-100 `RiskScore`
- `baseline_engine.py`     -- rolling 30-day baselines + peer centroids
- `governance.py`          -- four-stage update governance check (Drift, Peer, Trend, Suspicion)
- `train_all.py`           -- unified single-command runner for model training on MacBook

Risk Fusion Formula:
  $$\text{RiskScore} = (0.35 \cdot P_{\text{xgb}} + 0.25 \cdot S_{\text{IF}} + 0.20 \cdot D_{\text{peer}} + 0.15 \cdot D_{\text{user}} + 0.05 \cdot D_{\text{drift}}) \times 100$$

Baseline Governance Stages:
  1. Drift rate check
  2. Peer-anchor divergence
  3. Monotonic trend (7-day window)
  4. Suspicion threshold (>0.6 = suppress)

---

### Layer 3: Backend Layer (Django)
**Responsibility:** Serve data to the frontend, manage async LLM tasks, persist everything.

Framework: Django 4.2 LTS + Django REST Framework 3.15
Async tasks: Celery 5.3 + Redis 7 as broker
Database: SQLite 3 (Dev mode) / PostgreSQL 15 (MacBook / Production)

Django Apps:
- `users/`        -- `UserProfile`, `PeerGroup` models
- `alerts/`       -- `Alert`, `RiskScore`, `SHAPValue` models
- `baselines/`    -- `UserBaseline`, `GovernanceLog` models
- `explanations/` -- `Explanation`, `ChatSession`, `ChatMessage` models
- `verdicts/`     -- `AnalystVerdict` model
- `metrics/`      -- `ExperimentResult` model

API Base URL: `/api/v1/`

Key REST Endpoints:
  `GET  /api/v1/users/`                    -- list all users with latest risk score
  `GET  /api/v1/users/{id}/profile/`       -- user profile + 30-day history
  `GET  /api/v1/alerts/`                   -- paginated alert feed
  `GET  /api/v1/alerts/{id}/explanation/`  -- fetch LLM explanation for alert
  `POST /api/v1/alerts/{id}/verdict/`      -- submit TP/FP analyst verdict
  `POST /api/v1/chat/{session_id}/`        -- send message to analyst chatbot
  `GET  /api/v1/metrics/`                  -- confusion matrix, F1, AUC
  `GET  /api/v1/experiments/`              -- E1-E5 result tables

---

### Layer 4: Async Task Layer (Celery)
**Responsibility:** Handle slow LLM API calls without blocking the dashboard.

Tasks:
- `generate_explanation.delay(alert_id)`  -- builds evidence object, calls Claude API
- `evaluate_faithfulness.delay(exp_id)`   -- runs FaithLens rubric check
- `run_governance_check.delay()`          -- weekly baseline governance (scheduled)

---

### Layer 5: Presentation Layer (React)
**Responsibility:** Analyst-facing web dashboard.

Framework: React 18 + Tailwind CSS + Recharts
Build tool: Vite
State management: React Context API (lightweight)
HTTP client: Axios

Pages and routes:
  `/`                    -- Risk Dashboard (leaderboard + alert feed)
  `/users/:id`           -- User Profile (gauge + history chart)
  `/timeline`            -- Incident Timeline (event log + filters)
  `/alerts/:id/chat`     -- AI Chatbot Panel (explanation + Q&A)
  `/feedback`            -- Analyst Feedback (verdict submission)
  `/admin/metrics`       -- Admin Metrics (confusion matrix, AUC, F1)

---

## 4. Tech Stack Summary

| Component | Technology | Version | Why |
|---|---|---|---|
| ML Pipeline | scikit-learn, XGBoost, SHAP | latest stable | Academic standard for CERT research |
| Data Processing | pandas, NumPy | latest stable | Standard data engineering |
| Class Imbalance | imbalanced-learn (SMOTE) | latest stable | CERT dataset is ~1-2% malicious |
| Model Storage | joblib | latest stable | Fast numpy array serialisation |
| Backend | Django + DRF | 4.2 LTS + 3.15 | Battle-tested, excellent REST support |
| Async Tasks | Celery | 5.3 | Non-blocking LLM calls |
| Task Broker | Redis | 7 | Fast in-memory queue |
| Database | SQLite (Dev) / PostgreSQL 15 | 15 | Lightweight local dev & robust deployment |
| LLM API | Anthropic Claude API | via anthropic SDK | Evidence-constrained explanations |
| Frontend | React | 18 | Industry standard, component model |
| Styling | Tailwind CSS | 3.x | Utility-first, fast development |
| Charts | Recharts | latest | React-native charting library |
| Bundler | Vite | latest | Fast HMR for development |
| Containerisation | Docker + docker-compose | latest | One-command reproducible deployment |

