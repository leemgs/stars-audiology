# STARS code

This folder contains the reproducible scaffold for the STARS **pre-analysis
study protocol**. It runs end-to-end on synthetic data (no restricted files) and
encodes the protocol's prespecified design decisions in code so the plan is
auditable, not just described in prose.

## What is implemented

- **Variable schema with DAG roles** (`src/variable_schema.py`): exposure /
  confounder / mediator labels, the minimal-sufficient vs. extended adjustment
  sets, separated endpoints, and cross-national measurement-comparability ratings
  (with a `transportable_predictors()` filter for the common model).
- **Fixed study config** (`config/study_config.yaml`): pinned survey cycles, age
  window (40–69), audiometry frequencies, endpoints, hearing-loss cutoffs
  (primary 25 dB HL), external-validation plan, and fairness subgroups.
- Dataset harmonization helpers and PTA feature derivation.
- **Survey-aware baseline models** (`src/modeling.py`) reporting discrimination,
  Brier, and **calibration-in-the-large and calibration slope** (separately).
- Synthetic smoke test proving the code runs without raw medical data.
- MedGemma-style fixed-schema clinical-text extraction template (`src/llm_extract.py`).
- **LLM extraction evaluation** (`src/llm_eval.py`): per-field exact match,
  precision/recall/F1, omission, evidence-span agreement, document-level match,
  run-to-run consistency, and a referral-critical (clinically significant) error rate.
- **Deterministic red-flag safety layer** (`src/safety.py`) with an **evaluation
  harness** (`src/test_safety.py`) reporting sensitivity (recall), specificity,
  over-referral, subgroup performance, vignette composition, and the finite-set caveat.

## What is not included

- Raw KNHANES files, because users should download them from KDCA under the official access procedure
- Raw clinical records
- Any diagnostic or treatment model

## Recommended analysis order

1. Download KNHANES and NHANES files.
2. Create dataset-specific mapping YAML files.
3. Harmonize into the common schema.
4. Run weighted association analyses.
5. Train baseline models on KNHANES.
6. Validate on NHANES.
7. Only after IRB approval, test the LLM extraction module on deidentified hospital notes.

## Real NHANES results (turnkey)

`src/nhanes_analysis.py` runs the **real** survey-weighted NHANES analysis and
writes both a results JSON and a LaTeX table that the manuscript auto-includes.
NHANES public-use files are free from the U.S. CDC (no account needed). Because
some sandboxes block outbound access to `wwwn.cdc.gov`, either download the files
yourself into `data/raw/nhanes/<cycle>/` or pass `--download` where access is
allowed.

```bash
# Files needed per cycle (e.g., 2017-2018 → suffix _J):
#   DEMO_J.XPT  AUQ_J.XPT  AUX_J.XPT  DPQ_J.XPT   (place in data/raw/nhanes/2017-2018/)
python src/nhanes_analysis.py \
    --cycles 2011-2012 2015-2016 2017-2018 \
    --data-dir data/raw/nhanes \
    --out outputs/nhanes_results.json \
    --latex ../paper/tables/table_results.tex
cd ../paper && bash build.sh     # the real results table now appears in the PDF
```

The estimators (Taylor-linearized survey prevalence; design-based cluster-robust
logistic) are unit-tested for correctness:

```bash
python src/test_nhanes_analysis.py     # validates the survey math on structured data
```

## Real KNHANES results (primary development cohort)

KNHANES is the **primary** cohort because it carries a general perceived-stress
item (NHANES does not), so it is where STARS's primary perceived-stress exposure
is tested. KNHANES microdata require official KDCA approval and cannot be
auto-downloaded. The loader is **mapping-driven**: complete
`config/knhanes_mapping.yaml` from the codebook for your cycles, place the
approved `.sas7bdat` files under `data/raw/knhanes/<cycle>/`, then run:

```bash
python src/knhanes_analysis.py \
    --mapping config/knhanes_mapping.yaml \
    --data-dir data/raw/knhanes --cycles 2010 2011 2012 \
    --out outputs/knhanes_results.json \
    --latex ../paper/tables/table_results_knhanes.tex
cd ../paper && bash build.sh     # the KNHANES results table then appears in the PDF
```

It reuses the same validated design-based estimators as the NHANES pipeline and
derives `perceived_stress` as the primary exposure. Derivation logic is
unit-tested on a synthetic KNHANES-shaped frame:

```bash
python src/test_knhanes_analysis.py
```

## Safety layer

The red-flag layer is deterministic and independent of any probabilistic
model. A low predicted risk must never suppress urgent referral. The harness
reports sensitivity, specificity, over-referral, and subgroup recall, and prints
the explicit caveat that finite-set sensitivity of 1.00 is a target, not a
guarantee of zero deployment misses. Verify it with:

```bash
python src/test_safety.py        # sensitivity/specificity/over-referral + caveat
python src/llm_eval.py           # per-field extraction-metric self-check
# or, if pytest is installed:
python -m pytest src/test_safety.py
```
