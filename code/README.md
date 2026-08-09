# STARS code

Reproducible scaffold for the STARS **survey-weighted research study** (primary
KNHANES result) and its **prespecified plan** for prospective components. It runs
end-to-end on synthetic data (no restricted files) and encodes the study's
prespecified design decisions in code so the analysis is auditable, not just
described in prose. This README documents how to **reproduce every analysis** —
including how to obtain the two national surveys.

## What is implemented

- **Variable schema with DAG roles** (`src/variable_schema.py`): exposure /
  confounder / mediator labels, minimal-sufficient vs. extended adjustment sets,
  separated endpoints, and cross-national measurement-comparability ratings.
- **Fixed study config** (`config/study_config.yaml`): pinned survey cycles, age
  window (40–69), audiometry frequencies, endpoints, hearing-loss cutoffs, the
  external-validation plan, and fairness subgroups.
- **Design-based survey estimators** (`src/nhanes_analysis.py`): Taylor-linearized
  weighted prevalence and cluster-robust survey logistic — reused by both cohorts.
  Support **domain (subpopulation) estimation** on the full design and a
  conservative **single-PSU centering** option; cross-checkable in R `survey`
  via `src/reproduce_survey.R`.
- **NHANES pipeline** (`src/nhanes_analysis.py`) and **KNHANES pipeline**
  (`src/knhanes_analysis.py`, mapping-driven) that emit a results JSON and a LaTeX
  table the manuscript auto-includes.
- **Baseline models** (`src/modeling.py`): discrimination, Brier, calibration-in-
  the-large, and calibration slope.
- **SAFE-EAR safety/extraction stack (Paper B)** — an open 71-case red-flag
  benchmark (`src/redflag_benchmark.py`), a **deterministic guideline-derived
  safety layer** (`src/safety.py`), schema-constrained extraction
  (`src/llm_extract.py`, `src/llm_eval.py`), and a real open-medical-LLM
  extractor (`src/llm_medgemma.py`, `google/medgemma-4b-it`). A **unified runner**
  (`src/run_llm_eval.py`) scores the rule-based references *and* MedGemma through
  one harness (end-to-end recall **naive 56% → MedGemma 78% → tuned 100%**);
  tests in `src/test_safety.py` and `src/test_llm_medgemma.py`. See
  `notebooks/medgemma_eval_colab.ipynb` to reproduce the MedGemma row on a free GPU.

---

## 0. Environment setup

Python ≥ 3.10. Use a virtual environment (recommended) or `--break-system-packages`.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# KNHANES SAS files additionally need a robust reader:
pip install pyreadstat
```

Provenance: analyses are deterministic (fixed seeds); the exact cycles are pinned
in `config/`. Raw survey files are **never** committed (see `.gitignore`); only
derived results (JSON) and generated LaTeX tables are.

---

## 1. Reproduce the NHANES analysis (public; no account)

NHANES public-use files are free from the U.S. CDC. Since 2024 they live at
`https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/<year>/DataFiles/<FILE>.xpt`
(the pipeline tries the current and legacy URL layouts automatically).

```bash
# Auto-download where outbound access to wwwn.cdc.gov is allowed:
python src/nhanes_analysis.py \
    --cycles 2011-2012 2015-2016 2017-2018 \
    --data-dir data/raw/nhanes --download \
    --out outputs/nhanes_results.json \
    --latex ../paper/tables/table_results.tex
cd ../paper && bash build.sh          # the real results table appears in the PDF
```

If a network blocks the CDC host, download the four files per cycle in a browser
(`DEMO`, `AUQ`, `AUX`, `DPQ`; suffix `_G`=2011-12, `_I`=2015-16, `_J`=2017-18)
into `data/raw/nhanes/<cycle>/` and run **without** `--download`.

Validate the survey math (no data needed):

```bash
python src/test_nhanes_analysis.py
```

---

## 2. Reproduce the KNHANES analysis (primary cohort; KDCA approval)

KNHANES is the **primary** development cohort: unlike NHANES it carries a general
perceived-stress item (`BP1`), so it is where STARS's primary perceived-stress
exposure is tested. The microdata require official KDCA approval and cannot be
redistributed or auto-downloaded — follow these steps.

### Step 1 — Obtain the raw data (KDCA)

1. Go to the KNHANES raw-data portal: <https://knhanes.kdca.go.kr>
2. **자료실 → 원시자료 다운로드**: create an account and submit the
   **원시자료 이용 동의서** (data-use agreement). Approval can take time.
3. Download the yearly **SAS** files for **2010, 2011, 2012** (KNHANES V-1/2/3).
   ⚠️ The tinnitus and pure-tone-audiometry items are in the **otology / ENT
   examination (이비인후과 검진)** module — confirm the download includes that
   examination (it may be a combined yearly file or a separate ENT file).
4. Also download the **codebook (이용지침서)** to confirm the exact variable
   names for tinnitus (`HtE_1`), occupational noise (`HtE_5`), audiometry
   (`O_R_500` …), and the otology-exam weight.

### Step 2 — Place the files

```bash
mkdir -p data/raw/knhanes/{2010,2011,2012}
# copy the approved SAS files, e.g.:
#   data/raw/knhanes/2010/HN10_ALL.sas7bdat
#   data/raw/knhanes/2011/HN11_ALL.sas7bdat
#   data/raw/knhanes/2012/HN12_ALL.sas7bdat
```

If your filenames differ (e.g., lowercase `hn10_all.sas7bdat`, or a separate ENT
file), edit the `files:` block in `config/knhanes_mapping.yaml` to match.

### Step 3 — Confirm the variable mapping

`config/knhanes_mapping.yaml` is pre-filled with best-known KNHANES codes tagged
by confidence. Confirm the **LIKELY/VERIFY** rows against your codebook:

Values below reflect the codebook-verified mapping in `config/knhanes_mapping.yaml`
(the tinnitus/audiometry/noise items live in the separate **이비인후검사 (ENT)**
file, merged on the person id by the loader):

| Field | Pre-filled | Confidence / action |
|-------|-----------|---------------------|
| `perceived_stress` | `BP1` (1–2 = high) | CONFIRMED |
| `depressed_2wk` | `BP5` | CONFIRMED |
| `age`,`sex`,`edu`,`ho_incm`,`occp` | as named | CONFIRMED |
| `employment` | `EC_stt_1` | LIKELY — confirm |
| `tinnitus_item` | `T_Q_VN` (1 = yes, 2 = no) | CONFIRMED (ENT file) |
| `bothersome_item` | `T_Q_VN1` (2,3 = annoying) | CONFIRMED (ENT file) |
| `occupational_noise` | `T_NQ_OCP` (1 = yes) | CONFIRMED (ENT file) |
| audiometry | `T_HR###_rt`/`T_HR###_lt` | CONFIRMED (ENT file; clean dB, NaN = not tested) |
| `weight` | `wt_itvex` (pool: `/n_years`) | CONFIRMED in ALL file; no ENT-specific weight released (see Mo2) |
| `strata`,`psu` | `kstrata`,`psu` | CONFIRMED |
| `sleep_hours` | `<FILL>` | FILL (optional; mediator only) |

### Step 4 — Run and inspect coverage

```bash
python src/knhanes_analysis.py \
    --mapping config/knhanes_mapping.yaml \
    --data-dir data/raw/knhanes --cycles 2010 2011 2012 \
    --out outputs/knhanes_results.json \
    --latex ../paper/tables/table_results_knhanes.tex \
    --latex-extended ../paper/tables/table_extended_knhanes.tex \
    --dump-analytic outputs/knhanes_analytic.csv
cd ../paper && bash build.sh          # the KNHANES results + extended tables appear
```

`--latex-extended` regenerates the extended/sensitivity table (mediator-adjusted,
hearing-loss-adjusted, worse-ear, and high-frequency models) in place, replacing
the `[pending data run]` placeholders. `--dump-analytic` writes the derived
analytic frame so the design-based SEs can be **independently reproduced** in the
R `survey` package (M6):

```bash
Rscript src/reproduce_survey.R outputs/knhanes_analytic.csv
```

The run prints a **`Derived-variable coverage (non-null counts)`** report. Use it
to confirm the mapping resolved correctly:

- A variable showing **0** (e.g., `tinnitus : 0`) means its code in the mapping
  does not exist in your file → correct it from the codebook and re-run.
- Non-zero counts in the thousands mean the mapping is good.

Validate the derivation logic (no data needed):

```bash
python src/test_knhanes_analysis.py
```

### Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `FileNotFoundError: Missing …/HN10_ALL.sas7bdat` | Raw file not in place; complete Step 1–2, or fix `files:` in the mapping. |
| `Could not read … install pyreadstat` | `pip install pyreadstat` (robust for Korean-encoded/compressed SAS). |
| `tinnitus`/`occ_noise` coverage = 0 | The ENT file was not merged, or `T_Q_VN`/`T_NQ_OCP` differ in your cycle → confirm the ENT file is present and the codes from the codebook. |
| Prevalence looks off | Confirm `wt_itvex` was pooled correctly (divided by the number of years); KDCA released no ENT-specific weight, so the interview+exam weight is used (see Mo2 in the manuscript). |

---

## 3. Safety layer and self-checks

The red-flag layer is deterministic and independent of any model; a low predicted
risk must never suppress urgent referral. The harness reports sensitivity,
specificity, over-referral, and subgroup recall, and prints the caveat that
finite-set sensitivity of 1.00 is a target, not a guarantee of zero deployment
misses.

```bash
python src/test_safety.py        # sensitivity/specificity/over-referral + caveat
python src/llm_eval.py           # per-field extraction-metric self-check
python src/run_pipeline.py --config config/study_config.yaml   # synthetic smoke test
```

## What is not included (by design)

- Raw KNHANES/NHANES files (obtain per each provider's terms; never committed).
- Raw clinical records; any diagnostic or treatment model.
