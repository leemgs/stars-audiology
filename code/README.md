# StressEar-AI code

This folder contains a reproducible starter pipeline for public dataset analysis and future clinical text extraction.

## What is implemented

- Common variable schema for tinnitus, hearing, stress, noise, and survey design features
- Dataset harmonization helpers
- PTA feature derivation
- Baseline risk-model pipeline
- Synthetic smoke test that proves the code runs without raw medical data
- MedGemma-style fixed-schema clinical text extraction prompt template
- Deterministic red-flag safety layer (`src/safety.py`) that overrides model
  output for SSNHL / neurologic warning signs, with a curated vignette test
  suite (`src/test_safety.py`) reporting red-flag recall

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
model. A low predicted risk must never suppress urgent referral. Verify it with:

```bash
python src/test_safety.py        # prints red-flag recall (target = 1.00)
# or, if pytest is installed:
python -m pytest src/test_safety.py
```
