# Research Paper 1: Contamination-Resistant Adaptive Baseline Governance

## Overview
- **Title:** Contamination-Resistant Adaptive Baseline Governance for Defending UEBA Systems Against Slow-Escalation Poisoning
- **Primary Research Focus:** Defending adaptive UEBA systems against slow-escalation baseline poisoning attacks while allowing legitimate behavioral drift.
- **Dataset:** CMU CERT Insider Threat Dataset r5.2 (692,645 daily vectors; 562,594 baseline fitting / 130,051 evaluation records across 44 behavioral features).
- **Key Experiments:** E2 (Ungoverned Poisoning Simulation), E3 (Governed Poisoning Defense Validation), E4 (Legitimate Role Change vs. Malicious Drift Classification).

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
- Governance Engine: `backend/ml/baseline/governance.py`
- Baseline Engine: `backend/ml/baseline/baseline_engine.py`
- Experiment E2: `backend/ml/experiments/e2_poisoning_simulation.py`
- Experiment E3: `backend/ml/experiments/e3_governance_validation.py`
- Experiment E4: `backend/ml/experiments/e4_drift_classification.py`
- Database Seed & Fixtures: `backend/ml/data/seed_sqlite_db.py`
