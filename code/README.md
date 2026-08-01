# StressEar-AI code

This folder contains the reproducible scaffold for the StressEar-AI **pre-analysis
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
