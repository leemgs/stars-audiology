<p align="center">
  <img src="./stars-audiology.png" alt="STARS — Stress, Tinnitus, and Audiometric Research Study" width="100%">
</p>

# STARS

**STARS** = **S**tress, **T**innitus, and **A**udiometric **R**esearch **S**tudy.

An *American Journal of Audiology*–targeted **survey-weighted research study** on
the associations among perceived stress / work-related factors, tinnitus, and
hearing outcomes, using public survey data. Its primary finding (real KNHANES,
adults 40–69): perceived stress tracks the tinnitus *symptom* (OR 1.42) but not
the audiometric *threshold* (OR 1.18, ns) once occupational noise and age are
accounted for, with NHANES as directional support. A prespecified plan for
prospective components — cross-national validation and a clinician-governed,
safety-gated AI/referral component — is specified but carries no results.
Perceived stress is treated as *associated* with — not a proven cause of —
tinnitus/hearing outcomes.

Repository: <https://github.com/leemgs/stars-audiology>

## Two papers

This repository holds **two companion manuscripts**:

- **Paper A — STARS** (`paper/`, targeted at *American Journal of Audiology*): the
  empirical, survey-weighted finding above, with the AI/safety component demoted
  to a prospective plan (no results).
- **Paper B — SAFE-EAR** (`paper02/`, targeted at a medical-informatics venue):
  develops that AI/safety component **with real results** — a deterministic,
  guideline-derived referral-safety layer over open-LLM extraction, evaluated on
  an open 71-case benchmark (no patient data). Rule coverage is 100%; end-to-end
  safety is bounded by extraction, and the benchmark *discriminates* it (red-flag
  recall 56% → 100% across a naive vs. an improved extractor). An actual MedGemma
  evaluation is prospective; the benchmark and metrics are fixed as a prespecified
  reference.

| Folder | What it contains |
|--------|------------------|
| `paper/`   | **Paper A (STARS)** — LaTeX manuscript (source sections, bibliography, tables, figures) and the compiled PDF: the empirical stress–tinnitus–threshold survey study. |
| `paper02/` | **Paper B (SAFE-EAR)** — LaTeX manuscript, auto-generated result tables, result JSONs, and compiled PDF: the deterministic referral-safety layer and open benchmark, with real results. |
| `code/`    | Reproducible pipeline shared by both papers: survey-weighted NHANES/KNHANES analysis (Paper A) and the red-flag safety layer, open benchmark, rule-based extractors, and evaluation harness (Paper B), with tests. |
| `ppt/`     | English and Korean presentation decks (`pptxgenjs` source scripts + built `.pptx`). |
