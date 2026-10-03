# Research Paper 2: Hybrid Multimodal Risk Fusion and Explainable UEBA

## Overview
- **Title:** Hybrid Multimodal Risk Fusion and Evidence-Grounded Explainable UEBA for SOC Incident Triage
- **Primary Research Focus:** The hybrid UEBA detection pipeline, multi-model risk fusion, post-hoc SHAP feature attribution, evidence-grounded LLM explanations, and SOC analyst workflow.
- **Dataset:** CMU CERT Insider Threat Dataset r5.2 (692,645 total vectors; 562,594 train / 130,051 test across 44 behavioral features).
- **Key Empirical Results:**
  - Full-Scale Held-Out Evaluation (130,051 test records): 99.78% Detection Recall (3,705 threats caught, 8 missed), 100.00% Precision (0 false alarms), 0.9989 empirical F1-score.
  - Experiment E1 (Model Comparison): Hybrid Fusion (F1 0.9412, AUC 0.9782) vs. Standalone XGBoost+SMOTE (F1 0.8885, AUC 0.9415) and SVM (F1 0.7879, AUC 0.8842).
  - Experiment E5 (FaithLens Faithfulness Audit): 0.9555 overall score (97.17% Factuality, 97.67% Directional Consistency, 90.00% Completeness).

## File Manifest
- `main.tex`: Primary LaTeX source file (IEEEtran conference/journal style).
- `references.bib`: BibTeX bibliography file containing accurate citations for all referenced papers.

## How to Compile
### In Overleaf:
1. Create a New Project -> "Upload Project".
2. Upload `main.tex` and `references.bib`.
3. Set the compiler to `pdfLaTeX` (standard default).
4. Click `Recompile`.

### Local LaTeX Environment (MiKTeX / TeX Live):
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Source Code Traceability
- Feature Engineering: `backend/ml/data/feature_engineer.py`
- Chronological Splitter: `backend/ml/data/splitter.py`
- SVM Model: `backend/ml/models/svm_model.py`
- XGBoost + SMOTE: `backend/ml/models/xgboost_model.py`
- Isolation Forest: `backend/ml/models/isolation_forest.py`
- Risk Fusion Engine: `backend/ml/models/risk_fusion.py`
- SHAP Explainer: `backend/ml/models/shap_explainer.py`
- Evidence Builder: `backend/apps/explanations/evidence_builder.py`
- Claude LLM Client: `backend/apps/explanations/llm_client.py`
- Celery Async Tasks: `backend/tasks/explanation_tasks.py`
- Experiment E1: `backend/ml/experiments/e1_model_comparison.py`
- Experiment E5: `backend/ml/experiments/e5_faithfulness_eval.py`
- Database Seed & Fixtures: `backend/ml/data/seed_sqlite_db.py`
