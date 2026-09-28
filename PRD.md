# Product Requirements Document (PRD)
## AI-Powered Adaptive UEBA for Insider Threat and Account Compromise Detection

---

## 1. Project Overview

**Project Name:** Adaptive UEBA -- Insider Threat Detection System
**Degree:** M.Tech (Master of Technology)
**Academic Year:** 2026-2027
**Dataset:** CMU CERT Insider Threat Dataset r5.2
**Stack:** Python 3.11, Django 4.2, React 18, PostgreSQL 15, Redis 7, Docker

### Problem Being Solved
Adaptive UEBA baselines that continuously update themselves are vulnerable to slow-escalation poisoning. An attacker who increments malicious behaviour by ~5% per month causes the model to silently absorb the escalation as new normal. No peer-reviewed system on the CERT dataset defends against this specific attack class. This project builds the defence.

### Primary Research Contribution
A contamination-resistant baseline governance engine that sits on top of a hybrid ML detection pipeline and blocks poisoned baseline updates while allowing legitimate behavioural drift (e.g., role changes) to pass through.

---

## 2. Users

| User | Role | Primary Need |
|---|---|---|
| Security Analyst | Reviews alerts and risk scores | Fast, explainable alert triage |
| Admin / Researcher | Monitors model performance | Confusion matrix, AUC, F1 metrics |
| Guide / Evaluator | Reviews research results | Experiment outputs and comparison tables |

---

## 3. Functional Requirements

### FR-1: Data Pipeline
- FR-1.1: Ingest all 6 CERT r5.2 CSV files (logon, file, email, http, device, psychometric)
- FR-1.2: Clean null values, normalise timestamps to UTC, deduplicate events
- FR-1.3: Engineer a daily user-feature matrix with minimum 40 features
- FR-1.4: Enforce a strict time-based train/test split (no random splitting)
- FR-1.5: Export processed feature matrix to PostgreSQL and CSV for reproducibility

### FR-2: Hybrid ML Engine
- FR-2.1: Train an SVM classifier as a baseline model
- FR-2.2: Train an XGBoost classifier with SMOTE oversampling for class imbalance
- FR-2.3: Run Isolation Forest for unsupervised anomaly scoring
- FR-2.4: Apply SHAP post-hoc to every XGBoost prediction
- FR-2.5: Output SHAP top-5 features per prediction as structured JSON
- FR-2.6: Fuse all model outputs into a single 0-100 RiskScore using the formula:
  RiskScore = (0.35*P_xgb + 0.25*S_IF + 0.20*D_peer + 0.15*D_user + 0.05*D_drift) x 100
- FR-2.7: Serialise all trained models with joblib for reuse

### FR-3: Contamination-Resistant Baseline Engine
- FR-3.1: Maintain a rolling 30-day per-user behavioural baseline
- FR-3.2: Maintain peer-group centroids clustered by job role and department
- FR-3.3: Run a four-stage governance check weekly before allowing baseline updates:
  - Stage 1: Drift rate monitoring
  - Stage 2: Peer-anchor divergence check
  - Stage 3: Monotonic trend detection (7-day window)
  - Stage 4: Drift suspicion scoring (suppress update if score > 0.6)
- FR-3.4: Log all suppressed updates with reason code to PostgreSQL
- FR-3.5: Distinguish legitimate drift (role change) from malicious escalation

### FR-4: LLM Explanation and Analyst Chatbot
- FR-4.1: Build a structured evidence object per alert (SHAP top-5, risk score, 7-day trend)
- FR-4.2: Pass only the evidence object to Claude API under a faithfulness-constraining system prompt
- FR-4.3: Generate a 3-5 sentence plain-English explanation per alert
- FR-4.4: Support multi-turn analyst Q&A with conversation history in PostgreSQL
- FR-4.5: Handle all LLM API calls asynchronously via Celery + Redis
- FR-4.6: Evaluate 30 explanations using FaithLens faithfulness rubric (Experiment E5)

### FR-5: Django REST API
- FR-5.1: Expose REST endpoints for: users, alerts, risk scores, SHAP values, explanations, verdicts, metrics
- FR-5.2: Support pagination, filtering, and sorting on all list endpoints
- FR-5.3: Return all responses in JSON format with consistent error structure
- FR-5.4: Manage async LLM tasks via Celery task queue

### FR-6: React Dashboard (6 Pages)
- FR-6.1: Risk Dashboard -- top-risk user leaderboard + live alert feed
- FR-6.2: User Profile -- risk gauge, 30-day score history chart, feature breakdown
- FR-6.3: Incident Timeline -- chronological event log with filter controls
- FR-6.4: AI Chatbot Panel -- LLM explanation viewer + multi-turn Q&A
- FR-6.5: Analyst Feedback -- TP/FP verdict submission per alert
- FR-6.6: Admin Metrics -- confusion matrix, F1, AUC, experiment result tables

### FR-7: Research Experiments
- FR-7.1: E1 -- SVM vs XGBoost vs Hybrid comparison table (Precision, Recall, F1, AUC)
- FR-7.2: E2 -- 5%-per-month escalation poisoning simulation; measure baseline contamination
- FR-7.3: E3 -- Run E2 with governance engine active; compare detection rate
- FR-7.4: E4 -- Legitimate role-change vs malicious escalation classification accuracy
- FR-7.5: E5 -- Faithfulness evaluation of 30 LLM explanations using FaithLens rubric

---

## 4. Non-Functional Requirements

| Requirement | Target |
|---|---|
| AUC | >= 0.90 (benchmark: BRITD 0.9730) |
| F1-score | >= 0.85 (benchmark: MDPI adaptive 0.66) |
| Explanation Faithfulness | >= 0.85 (FaithLens rubric) |
| Dashboard page load | < 2 seconds |
| LLM explanation generation | < 30 seconds (async, non-blocking) |
| Reproducibility | Full stack runs from docker-compose up |
| Code quality | PEP8 compliant, all functions documented |

---

## 5. Out of Scope

- Real-time network stream processing (Kafka, Kinesis)
- Live Active Directory sync
- Graph Neural Networks (GNNs)
- Online model retraining
- Multi-tenant authentication / RBAC
- Mobile application
- Deployment to cloud (AWS/GCP/Azure)

---

## 6. Success Criteria

| Criterion | Measured By |
|---|---|
| Detection pipeline works | E1 produces Precision/Recall/F1/AUC table |
| Contamination resistance proven | E2 shows degradation; E3 shows recovery |
| Drift classification works | E4 accuracy score |
| LLM explanations are faithful | E5 FaithLens score >= 0.85 |
| System is demonstrable | Full stack runs via Docker |
| Research is publishable | Results suitable for Scopus-indexed journal |
