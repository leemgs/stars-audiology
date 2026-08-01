# StressEar-AI: Perceived Stress, Work-Related Factors, Tinnitus, and Hearing Outcomes

**Version 0.8 — American Journal of Audiology (AJA)-targeted study protocol / pre-analysis plan.**

StressEar-AI (Stress–Ear Artificial Intelligence) is a **pre-analysis study
protocol** (no empirical results) and reproducible code base for openly accessible
public-data analyses of the associations among **perceived stress and work-related
factors**, tinnitus, and hearing outcomes, plus a clinician-verified, safety-gated
AI component. Because the surveys lack validated job-strain instruments, the
exposure is labeled perceived stress (not measured occupational stress) and is
treated as **associated** with tinnitus/hearing outcomes, not as a proven cause.
All quantitative values in the package are **synthetic pipeline checks** with no
clinical meaning.

Repository: <https://github.com/leemgs/stress-ear-ai>

```text
.
├── paper/   LaTeX manuscript, bibliography, tables, figure, and compiled PDF
├── code/    Reproducible analysis code, LLM extraction template, safety layer
└── ppt/     English and Korean presentation decks (source + built .pptx)
```

The three working folders are described in detail below.

---

## 📄 `paper/` — the manuscript

The full LaTeX source of the AJA-targeted manuscript and its compiled PDF. The
document is modular: `main.tex` is the driver that pulls in each section and
table.

| Path | Contents |
|------|----------|
| `main.tex` | Driver file: document class, title page, running head, and `\input` of every section/table. |
| `build.sh` | Build script (`pdflatex` → `bibtex` → `pdflatex` ×2) producing the versioned PDF. |
| `references.bib` | BibTeX database of all cited works. |
| `sections/` | One `.tex` file per section: `abstract`, `introduction`, `related_work`, `public_data`, `methods`, `ai_system`, `results`, `discussion`, `conclusion`, `declarations`, `figures` (TikZ framework + causal DAG), and `references_manual`. |
| `tables/` | Standalone tables: `table_datasets`, `table_variables`, `table_harmonization` (cross-national mapping + comparability), `table_intended_use` (model intended use), `table_ai`, `table_metrics`, `table_redflag` (safety-eval plan). |
| `StressEar-AI_AJA_public_dataset_manuscript_v0.8.pdf` | Compiled manuscript (34 pp.). |

**Build the manuscript:**

```bash
cd paper
bash build.sh   # → StressEar-AI_AJA_public_dataset_manuscript_v0.8.pdf
```

Requires a TeX distribution with `lmodern`, `natbib`, `tikz`, and `microtype`.

---

## 💻 `code/` — reproducible analysis pipeline

A reproducible scaffold for the KNHANES/NHANES analyses, an open medical-LLM
extraction template, and the deterministic clinical-safety layer. It runs
end-to-end on synthetic data so anyone can exercise the pipeline **without any
restricted medical data**.

| Path | Contents |
|------|----------|
| `README.md` | Code-specific instructions and recommended analysis order. |
| `requirements.txt` | Python dependencies (pandas, scikit-learn, statsmodels, transformers, …). |
| `config/study_config.yaml` | Prespecified design: fixed survey cycles, age window (40–69), audiometry frequencies, separated endpoints, hearing-loss cutoffs, adjustment sets, external-validation plan, fairness subgroups, and LLM settings. |
| `src/variable_schema.py` | Harmonized schema with **DAG roles**, minimal vs. extended adjustment sets, separated endpoints, and cross-national comparability ratings. |
| `src/data_loaders.py` | Dataset harmonization helpers and pure-tone-average (PTA) feature derivation. |
| `src/modeling.py` | Survey-aware baseline models; AUROC, AUPRC, Brier, and **calibration-in-the-large & calibration slope**. |
| `src/run_pipeline.py` | Entry point; runs a synthetic smoke test of the full flow. |
| `src/nhanes_analysis.py` | **Real NHANES** survey-weighted pipeline: reads CDC public-use `.XPT` files and emits a results JSON + a LaTeX table the manuscript auto-includes. |
| `src/test_nhanes_analysis.py` | Correctness tests for the survey estimators (Taylor-linearized prevalence; design-based logistic). |
| `src/llm_extract.py` | MedGemma-style fixed-schema clinical-text extraction template. |
| `src/llm_eval.py` | **Extraction evaluation**: per-field exact match, P/R/F1, omission, span agreement, doc-level match, run consistency, referral-critical error rate. |
| `src/safety.py` | **Deterministic red-flag safety layer** (SSNHL / neurologic signs) that overrides model output to force urgent referral. |
| `src/test_safety.py` | Red-flag **evaluation harness**: sensitivity, specificity, over-referral, subgroups, vignette composition, finite-set caveat. |
| `outputs/` | Example metrics JSON from the synthetic smoke test. |

**Run the starter:**

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py --config config/study_config.yaml   # synthetic smoke test
python src/test_safety.py                                       # red-flag recall = 1.00
```

Download real KNHANES via the official KDCA portal and place files under
`code/data/raw/knhanes/`; NHANES public files can be fetched directly where URLs
are configured. Raw restricted data are never redistributed here.

---

## 📊 `ppt/` — presentation decks

Collaborator/clinician slide decks for sharing the framework with researchers and
Ajou University Hospital faculty. English and Korean versions share the same
layout, color system, and design; each is generated from a `pptxgenjs` script so
the decks are fully reproducible.

| Path | Contents |
|------|----------|
| `create_deck.js` | Source for the **English** deck (10 slides). |
| `create_deck_ko.js` | Source for the **Korean** deck (한글판, Malgun Gothic font). |
| `StressEar-AI_AJA_public_dataset_presentation_v0.8.pptx` | Built English deck. |
| `StressEar-AI_AJA_public_dataset_presentation_ko_v0.8.pptx` | Built Korean deck. |

Slides cover: title, core research question, dataset decision, analysis pipeline,
open-AI role, expected contributions, collaboration plan, aims & hypotheses,
rigor/reporting/safety, and closing.

**Rebuild the decks:**

```bash
cd ppt
npm install pptxgenjs
node create_deck.js      # English → StressEar-AI_AJA_public_dataset_presentation_v0.8.pptx
node create_deck_ko.js   # Korean  → StressEar-AI_AJA_public_dataset_presentation_ko_v0.8.pptx
```

---

## Primary public datasets

1. **KNHANES** — primary development dataset: Korean, population-based, with prior
   tinnitus/hearing epidemiology using audiometry and health questionnaires.
2. **NHANES** — geographic external-validation dataset: public audiometry,
   noise-exposure, tinnitus/hearing questionnaires, and rich covariates.

Treatment timing and recovery (e.g., the SSNHL "golden window") require the
prospective **Ajou University Hospital** clinical extension, not cross-sectional
public data.

## Ethics and safety

This package does not provide medical diagnosis or treatment advice. AI outputs are
restricted to research feature extraction, calibrated risk stratification, and
guideline-linked explanation templates, and are governed by a deterministic
red-flag referral layer. All clinical decisions remain with licensed clinicians.
Public-data analyses use deidentified survey microdata; the clinical extension
proceeds only under institutional review board approval.
