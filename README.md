# HEAR-WORK AI: Occupational Stress, Tinnitus, and Hearing Outcomes

**Version 0.7 — American Journal of Audiology (AJA)-targeted framework / pre-analysis protocol.**

This repository contains a submission-oriented manuscript package and reproducible
starter code for openly accessible public-data analyses of the associations among
occupational (psychosocial) stress, tinnitus, and hearing outcomes, plus a
clinician-verified, safety-gated AI component.

## Repository structure

```text
./README.md
./paper/   LaTeX manuscript, bibliography, tables, conceptual figure, and compiled PDF
./code/    Reproducible analysis code for KNHANES/NHANES, an open medical-LLM extraction
           template, and a deterministic red-flag safety layer with tests
./ppt/     Sharing deck for collaborators and Ajou University Hospital clinicians
```

## What is new in v0.7

- **Journal-ready manuscript.** Title page with article type, running head, word
  counts, and reporting-guideline declarations; a structured abstract; explicit
  **aims and prespecified hypotheses (H1–H3)**; an anonymized motivating clinical
  vignette; and a conceptual-framework **figure**.
- **Methodological rigor.** Reporting per **STROBE** and **TRIPOD+AI**; missing-data
  handling (multiple imputation); precision-based sample-size framing; a full
  prediction-model development/validation plan reporting **calibration, decision-curve
  utility, SHAP interpretability, and subgroup fairness**, not AUROC alone.
- **Clinical safety.** A deterministic **red-flag layer** (SSNHL / neurologic signs)
  that overrides probabilistic output so a low predicted risk can never suppress
  time-critical referral — the "golden-window" principle — backed by code and a
  vignette test suite (red-flag recall = 1.00).
- **Expanded references** to WHO, tinnitus and sudden-hearing-loss clinical practice
  guidelines, STROBE, and TRIPOD+AI.

## Primary public datasets selected

1. **KNHANES** — primary development dataset: Korean, population-based, with prior
   tinnitus/hearing epidemiology using audiometry and health questionnaires.
2. **NHANES** — geographic external-validation dataset: public audiometry,
   noise-exposure, tinnitus/hearing questionnaires, and rich covariates.

Occupational stress is treated as an exposure **associated** with tinnitus/hearing
outcomes, not as a proven direct cause. Treatment timing and recovery require the
prospective **Ajou University Hospital** clinical extension.

## Build the manuscript

```bash
cd paper
bash build.sh   # produces HEAR-WORK_AI_AJA_public_dataset_manuscript_v0.7.pdf
```

## Run the code starter

```bash
cd code
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py --config config/study_config.yaml   # synthetic smoke test
python src/test_safety.py                                       # red-flag recall = 1.00
```

The code is a reproducible scaffold. It does not redistribute restricted KNHANES
files: download KNHANES via the official KDCA portal and place files under
`code/data/raw/knhanes/`. NHANES public files can be fetched directly by the
scripts where URLs are configured. A synthetic-data path lets anyone exercise the
full pipeline without any restricted data.

## Rebuild the presentation

```bash
cd ppt
npm install pptxgenjs
node create_deck.js   # produces HEAR-WORK_AI_AJA_public_dataset_presentation_v0.7.pptx
```

## Ethics and safety

This package does not provide medical diagnosis or treatment advice. AI outputs are
restricted to research feature extraction, calibrated risk stratification, and
guideline-linked explanation templates, and are governed by a deterministic
red-flag referral layer. All clinical decisions remain with licensed clinicians.
Public-data analyses use deidentified survey microdata; the clinical extension
proceeds only under institutional review board approval.
