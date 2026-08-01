# StressEar-AI: Occupational Stress, Tinnitus, and Hearing Outcomes

**Version 0.7 — American Journal of Audiology (AJA)-targeted framework / pre-analysis protocol.**

StressEar-AI (Stress–Ear Artificial Intelligence) is a submission-oriented
manuscript package and reproducible code base for openly accessible public-data
analyses of the associations among occupational (psychosocial) stress, tinnitus,
and hearing outcomes, plus a clinician-verified, safety-gated AI component.
Occupational stress is treated as an exposure **associated** with tinnitus/hearing
outcomes, not as a proven direct cause.

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
| `sections/` | One `.tex` file per section: `abstract`, `introduction`, `related_work`, `public_data`, `methods`, `ai_system`, `results`, `discussion`, `conclusion`, `declarations`, `figures` (TikZ conceptual framework), and `references_manual` (rendered bibliography). |
| `tables/` | Standalone tables: `table_datasets`, `table_variables`, `table_ai`, `table_metrics`. |
| `StressEar-AI_AJA_public_dataset_manuscript_v0.7.pdf` | Compiled manuscript (26 pp.). |

**Build the manuscript:**

```bash
cd paper
bash build.sh   # → StressEar-AI_AJA_public_dataset_manuscript_v0.7.pdf
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
| `config/study_config.yaml` | Study configuration: dataset paths, age window, outcomes, survey-design variables, and LLM settings. |
| `src/variable_schema.py` | Common harmonized variable schema shared across datasets. |
| `src/data_loaders.py` | Dataset harmonization helpers and pure-tone-average (PTA) feature derivation. |
| `src/modeling.py` | Survey-aware baseline models and metric computation (AUROC, AUPRC, Brier). |
| `src/run_pipeline.py` | Entry point; runs a synthetic smoke test of the full flow. |
| `src/llm_extract.py` | MedGemma-style fixed-schema clinical-text extraction template. |
| `src/safety.py` | **Deterministic red-flag safety layer** (SSNHL / neurologic signs) that overrides model output to force urgent referral. |
| `src/test_safety.py` | Curated red-flag vignette test suite (red-flag recall target = 1.00). |
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
| `StressEar-AI_AJA_public_dataset_presentation_v0.7.pptx` | Built English deck. |
| `StressEar-AI_AJA_public_dataset_presentation_ko_v0.7.pptx` | Built Korean deck. |

Slides cover: title, core research question, dataset decision, analysis pipeline,
open-AI role, expected contributions, collaboration plan, aims & hypotheses,
rigor/reporting/safety, and closing.

**Rebuild the decks:**

```bash
cd ppt
npm install pptxgenjs
node create_deck.js      # English → StressEar-AI_AJA_public_dataset_presentation_v0.7.pptx
node create_deck_ko.js   # Korean  → StressEar-AI_AJA_public_dataset_presentation_ko_v0.7.pptx
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
