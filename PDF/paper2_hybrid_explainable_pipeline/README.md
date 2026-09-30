# Research Paper 2: Hybrid Multimodal Risk Fusion and Explainable UEBA

## Overview
- **Title:** Hybrid Multimodal Risk Fusion and Evidence-Grounded Explainable UEBA for SOC Incident Triage
- **Primary Research Focus:** The hybrid UEBA detection pipeline, multi-model risk fusion, post-hoc SHAP feature attribution, evidence-grounded LLM explanations, and SOC analyst workflow.
- **Dataset:** CMU CERT Insider Threat Dataset r5.2 (44 features across 6 log streams).
- **Key Experiments:** E1 (Model Comparison: SVM vs. XGBoost+SMOTE vs. Hybrid Fusion), E5 (FaithLens LLM Explanation Faithfulness Evaluation).

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
