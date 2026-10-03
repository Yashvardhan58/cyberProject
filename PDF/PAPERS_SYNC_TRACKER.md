# Parallel Research Papers Synchronization Tracker
**Project:** AI-Powered Adaptive UEBA for Insider Threat and Account Compromise Detection  
**Dataset:** Carnegie Mellon University (CMU) CERT Insider Threat Dataset r5.2  
**Author:** Chetan Shrikant Lokhande (PRN: 25PCS009)  
**Guide:** Prof. S. R. Patil  
**Institution:** D.K.T.E. Society's Textile and Engineering Institute, Ichalkaranji (Affiliated to Shivaji University, Kolhapur)  
**Workspace Path:** `D:\Chetan Sir\cyberProject\PDF\`

---

## 1. Two-Paper Parallel Architecture & Division of Concerns

| Attribute | Paper 1 | Paper 2 |
|---|---|---|
| **Folder Location** | `PDF/paper1_contamination_resistant_baseline/` | `PDF/paper2_hybrid_explainable_pipeline/` |
| **Working Title** | Contamination-Resistant Adaptive Baseline Governance for Defending UEBA Systems Against Slow-Escalation Poisoning | Hybrid Multimodal Risk Fusion and Evidence-Grounded Explainable UEBA for SOC Incident Triage |
| **Core Research Problem** | Adaptive UEBA baselines continuously absorb behavior, making them vulnerable to slow-rate adversarial poisoning (~5%/month escalation) | High false alarm rates and black-box ML opacity create severe triage bottlenecks in enterprise SOCs |
| **Primary Research Contribution** | 4-Stage Baseline Governance Engine that prevents slow-escalation poisoning while permitting legitimate organizational drift | Multi-model risk fusion with exact TreeSHAP attribution and FaithLens-verified evidence-grounded LLM explanations |
| **Key Architectural Assets** | • **Algorithm 1:** Four-Stage Baseline Update Governance (`alg:baseline_governance`)<br>• **Figure 1:** Governance Decision Workflow (`fig:governance_flow`) | • **Algorithm 1:** Hybrid Risk Fusion & Evidence Synthesis (`alg:alert_synthesis`)<br>• **Figure 1:** End-to-End Hybrid Explainable Pipeline (`fig:pipeline_arch`) |
| **Focus Topics** | • Threat model of $\alpha$-slow escalation<br>• Rolling 30-day baseline ($D_{\text{user}}$)<br>• Peer-group centroids ($D_{\text{peer}}$)<br>• 4-stage governance (Drift, Peer, Trend, Suspicion)<br>• Legitimate vs. malicious drift disambiguation | • 44-feature multimodal data engineering<br>• Chronological train/test splitting<br>• SMOTE-balanced XGBoost + SVM + Isolation Forest<br>• Risk fusion formula & severity tiers<br>• TreeSHAP local attribution<br>• Claude evidence grounding & FaithLens rubric<br>• Full-stack Django/React & Celery/Redis workflow |
| **Mapped Experiments** | **E2, E3, E4** | **E1, E5** |

---

## 2. Research Questions & Experiments Mapping

| ID | Research Question (RQ) | Experiment (E) | Affected Paper | Verified Result Summary | Source Module |
|---|---|---|---|---|---|
| **RQ1** | Does hybrid multi-model fusion outperform classical and standalone classifiers? | **E1: Model Comparison** | **Paper 2** | SVM: F1 0.7879, AUC 0.8842<br>XGBoost: F1 0.8885, AUC 0.9415<br>**Hybrid: F1 0.9412, AUC 0.9782** | `ml/experiments/e1_model_comparison.py` |
| **RQ1 (Scale)** | Does hybrid fusion maintain high precision/recall on full held-out test split? | **Operational Evaluation (130k test)** | **Paper 2** | **Recall: 99.78% (3,705/3,713 caught), Precision: 100.00% (0 FP), F1: 0.9989** across 130,051 held-out test user-days | `ml/models/train_all.py` |
| **RQ2** | Does an ungoverned adaptive baseline suffer statistical contamination under 5%/month poisoning? | **E2: Ungoverned Poisoning Simulation** | **Paper 1** | By Month 6, detection rate plummets from **94.0% to 22.0%**; baseline contamination reaches **89.0%** | `ml/experiments/e2_poisoning_simulation.py` |
| **RQ3** | Does the 4-stage governance engine prevent contamination and sustain detection rates? | **E3: Governed Defense Validation** | **Paper 1** | Sustains **~93.0% detection rate** throughout 6 months; suppresses **19 poisoned updates** | `ml/experiments/e3_governance_validation.py` |
| **RQ4** | Can the system distinguish legitimate role changes from malicious unilateral drift? | **E4: Drift Classification** | **Paper 1** | Accuracy: **94.00%**, Precision: **95.83%**, Recall: **92.00%**, False Suppression Rate: **4.00%** | `ml/experiments/e4_drift_classification.py` |
| **RQ5** | Can an LLM generate faithful, zero-hallucination explanations for security analysts? | **E5: FaithLens Faithfulness Audit** | **Paper 2** | Factuality: **97.17%**, Directional Consistency: **97.67%**, Completeness: **90.00%**<br>**Overall Faithfulness: 0.9555** (Target $\ge 0.85$ passed) | `ml/experiments/e5_faithfulness_eval.py` |

---

## 3. Verified Formulas, Parameters & Decision Boundaries

### Baseline Governance Engine (Paper 1)
- **Source:** `backend/ml/baseline/governance.py`
- **Suspicion Threshold ($\tau$):** `0.60`
- **Monotonic Trend Window ($K$):** `7 days`
- **Baseline Rolling Window ($W$):** `30 days`
- **Stage 1 Drift Acceleration Gain:** $\text{gain} = 5.0$, pass if $S_1 < 0.50$
- **Stage 2 Peer Divergence Gain:** $\text{gain} = 1.5$, pass if $S_2 < 0.45$
- **Stage 3 Monotonic Step Ratio:** fraction of $\delta_j \ge 0$, pass if $S_3 < 0.75$
- **Stage 4 Composite Score:**
  $$S_{\text{drift}} = 0.35 \cdot S_1 + 0.40 \cdot S_2 + 0.25 \cdot S_3$$
  - If $S_{\text{drift}} \ge 0.60 \implies \text{SUPPRESS}$ (Freeze baseline, trigger SOC alert)
  - If $S_{\text{drift}} < 0.60 \implies \text{ALLOW}$ (Update baseline)

### Multi-Model Risk Fusion Engine (Paper 2)
- **Source:** `backend/ml/models/risk_fusion.py`
- **Weights Formulation (Sum = 1.0):**
  $$RiskScore = (0.35 \cdot P_{\text{xgb}} + 0.25 \cdot S_{\text{IF}} + 0.20 \cdot D_{\text{peer}} + 0.15 \cdot D_{\text{user}} + 0.05 \cdot D_{\text{drift}}) \times 100$$
- **Severity Boundaries:**
  - $\text{CRITICAL}: \ge 80.0$
  - $\text{HIGH}: \ge 60.0 \text{ and } < 80.0$
  - $\text{MEDIUM}: \ge 30.0 \text{ and } < 60.0$
  - $\text{LOW}: < 30.0$

---

## 4. Current Status Matrix

| Module / Milestone | Implementation Status | Experimental Verification Status | Affects Paper 1 | Affects Paper 2 |
|---|---|---|---|---|
| Ingestion & Cleaning (6 CSVs) | Implemented (`cert_ingestor.py`, `cleaner.py`) | Verified on 692,645 rows | Baseline reference | Feature section |
| 44-Feature Daily Matrix | Implemented (`feature_engineer.py`) | Verified (692,645 vectors generated) | Feature reference | Core Methodology |
| Chronological Splitter | Implemented (`splitter.py`) | Verified (562,594 train / 130,051 test) | Methodology | Methodology |
| SVM Classifier | Implemented (`svm_model.py`) | Verified (50k sample, 2,072 SVs) | No | Section V |
| XGBoost + SMOTE Classifier | Implemented (`xgboost_model.py`) | Verified (Trained on 562,594 rows) | No | Section V |
| Isolation Forest Anomaly Scorer | Implemented (`isolation_forest.py`) | Verified (Trained on 562,594 rows) | No | Section V |
| Multi-Model Risk Fusion Engine | Implemented (`risk_fusion.py`) | Verified (Evaluated on 130,051 test rows) | Mentioned in context | Section V |
| 30-Day Rolling Baseline & Peer Centroid | Implemented (`baseline_engine.py`) | Verified (Fitted on 562,594 rows) | Core Architecture | Mentioned in context |
| 4-Stage Governance Engine | Implemented (`governance.py`) | Verified (E2, E3, E4) | Core Architecture | Mentioned in context |
| Local TreeSHAP Explainer | Implemented (`shap_explainer.py`) | Verified | No | Section VI |
| Evidence Builder Payload | Implemented (`evidence_builder.py`) | Verified (E5) | No | Section VI |
| Claude API Integration Client | Implemented (`llm_client.py`) | Verified (E5) | No | Section VI |
| Baseline Governance Task Queue (Celery) | Implemented (`apps/baselines/tasks.py`) | Verified | Section IV & Table 3 | No |
| LLM Explanation Task Queue (Celery) | Implemented (`apps/explanations/tasks.py`) | Verified (Unit tests 1-7) | No | Section VII & Table 3 |
| Django REST API Endpoints | Implemented (`backend/apps/`) | Verified | Architecture | Section VII |
| React 18 6-Page Dashboard | Implemented (`frontend/src/`) | Verified | No | Section VII |
| Full 15GB CERT Tarball Cluster Scale-Up | Pipeline Completed & Verified | **Completed (562k train / 130k test)** | Reflected in Paper 1 | Reflected in Paper 2 |

---

## 5. Ongoing Parallel Update Protocol
Whenever the project codebase is modified or new experiments are executed in the future:
1. **Zero Execution Constraint:** Do not run unnecessary DB/terminal commands; inspect code and result files directly.
2. **Impact Assessment:**
   - Changes to `governance.py`, `baseline_engine.py`, or experiments E2, E3, E4 $\implies$ Update **Paper 1**.
   - Changes to `risk_fusion.py`, `shap_explainer.py`, `evidence_builder.py`, `llm_client.py`, or experiments E1, E5 $\implies$ Update **Paper 2**.
   - Changes to data split or shared architecture $\implies$ Update methodology sections in both papers with distinct wording.
3. **Traceability Rule:** If a metric is unverified, mark as `TBD`. If text is removed, preserve in LaTeX using `%`.
