# KNHANES mapping verification (`knhanes_mapping.yaml`)

Pre-flight review of the default variable codes in `knhanes_mapping.yaml`,
cross-checked against **public** KNHANES codebook conventions (KNHANES IV–V,
2009–2012 otologic-exam cycles). The goal is to shrink the work you have to do
once the approved data + codebook arrive: for each field below, either you can
trust the default, or you know exactly which ones to look up.

> **Confidence legend**
> - ✅ **High** — matches well-established, stable KNHANES naming; low risk.
> - ⚠️ **Medium** — name is cycle-dependent or has a more standard alternative; **verify against the codebook for your exact cycles.**
> - ❓ **Unknown** — cannot be confirmed from public sources; **must be read from the otology-module codebook** that ships with the approved data.
>
> Confidence ≠ proof. Even ✅ items should be sanity-checked against the codebook
> PDF for the specific cycles you download, because KDCA occasionally renames
> variables between waves.

---

## Survey design

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `weight` | `wt_tot` | ⚠️ Medium | The standard **integrated** (exam + health-interview) weight in KNHANES is usually **`wt_itvex`**. Since STARS needs both the audiometry exam *and* the `BP1` stress interview item, the integrated weight is the correct one — `wt_itvex` is the more likely name than `wt_tot`. **Verify, and see the pooling note below.** |
| `strata` | `kstrata` | ✅ High | `kstrata` is the standard KNHANES variance stratum. |
| `psu` | `psu` | ✅ High | Standard primary sampling unit variable. |

**⚠️ Pooling correction (code-level, not a mapping field):** KDCA guidance is
that when you **pool multiple annual waves**, the integrated weight must be
divided by the number of years pooled (e.g., `wt_itvex / 3` for three cycles).
`knhanes_analysis.py` currently feeds the raw weight straight into `svy_mean` /
`svy_logistic` without this rescaling. This affects variance/CI width. Flag for
a one-line fix in the loader once the cycle count is fixed.

## Demographics (`common`)

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `age` | `age` | ✅ High | Standard. |
| `sex` | `sex` (1=M, 2=F) | ✅ High | Standard coding; the loader's `sex==2 → female` is correct. |
| `education` | `edu` | ✅ High | Standard education-level variable. |
| `income` | `ho_incm` | ✅ High | Household income **quartile**; `ho_incm5` is the quintile version if you want 5 groups. |
| `occupation` | `occp` | ✅ High | Standard occupation-reclassification variable. |
| `employment` | `EC_stt_1` | ⚠️ Medium | Economic-activity state exists in KNHANES, but the exact suffix varies by cycle — verify (`EC_stt_1` vs `EC_stt` etc.). |

## Exposure — perceived stress (**the primary STARS exposure**)

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `perceived_stress` | `BP1` | ✅ High | **Correct.** `BP1` is the KNHANES stress-perception item ("평소 스트레스 인지 정도"): 1 = feel very much, 2 = feel a lot, 3 = feel a little, 4 = hardly feel. |
| `stress_high_values` | `[1, 2]` | ✅ High | Dichotomizing "high stress" = {1,2} (much/very much) vs {3,4} is the standard, literature-consistent cut. |

## Mediators

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `depression_phq9_items` | `[]` (empty) | ✅ High | Correct to leave empty for **2009–2012** — the PHQ-9 module (`mh_PHQ_01`…`mh_PHQ_09`, sum `mh_PHQ_S`) was only added in later cycles (2014, 2016, 2018, 2020). If you later use a PHQ-9 cycle, fill these nine and the loader will prefer them. |
| `depressed_2wk` | `BP5` | ✅ High | **Correct.** `BP5` is the "felt sad/hopeless ≥ 2 weeks in the past year" item (1 = yes, 2 = no). The loader maps `1→1.0, 2→0.0` correctly. |
| `sleep_hours` | `Total_slp_wd` | ⚠️ Medium | `Total_slp_wd` (weekday mean sleep hours) exists from the **2016** sleep-module expansion onward. For **2009–2012** it likely does **not** exist; earlier waves used different sleep items. Verify per cycle; leave unmapped if absent (the loader tolerates a missing sleep variable). |

## Outcomes (**the two `<FILL>` fields — read from the codebook**)

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `tinnitus_item` | `<FILL>` | ❓ Unknown | **Must** be read from the otology-module codebook. This is the "ringing in the ears in the past year" question used to define tinnitus (the same construct Park et al., 2014 used on KNHANES 2009–2011). I cannot assert the exact variable name from public sources — do not guess; take it from the codebook. |
| `tinnitus_yes_values` | `[1]` | ⚠️ Medium | Plausible (1 = yes) but confirm the yes-code against the codebook. |
| `occupational_noise` | `<FILL>` | ❓ Unknown | Workplace loud-noise exposure question (the otology/occupational module). Read the exact code from the codebook; the loader maps `1→exposed, 2→not`. |

## Audiometry (pure-tone thresholds)

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `500`…`6000` right/left vars | `O_R_500` / `O_L_500`, … | ❓ Unknown | The `O_R_/O_L_<freq>` pattern is a **reasonable guess** at the otology exam's air-conduction threshold naming, but I cannot confirm the exact tokens (KNHANES has used variants). Verify all 12 names against the audiometry section of the codebook before trusting `better_ear_pta` / `worse_ear_pta`. |
| `invalid_threshold_codes` | `[999, 666]` | ⚠️ Medium | Non-response / could-not-test sentinel codes vary (also seen: `99999`, `888`). **Verify** — a wrong sentinel silently corrupts the PTA means, so this one matters. |
| `speech_freqs` | `["500","1000","2000","4000"]` | ✅ High | Standard speech-frequency PTA definition (0.5/1/2/4 kHz), consistent with the manuscript's PTA$_{0.5,1,2,4}$. |

## Files & analysis window

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `files.2010/2011/2012` | `HN10_ALL.sas7bdat`, `HN11_ALL.sas7bdat`, `HN12_ALL.sas7bdat` | ✅ High | Matches the standard KNHANES SAS release naming (`HN<yy>_ALL.sas7bdat`). |
| **2009 cycle** | *(intentionally absent)* | ✅ High | Resolved: the study window is **2010–2012 (KNHANES V)**. The protocol text (`study_config.yaml`, `methods.tex`, `public_data.tex`, `table_harmonization.tex`) was narrowed to match the mapping/CLI, so no 2009 file is needed. |
| `age_min/max` | `40 / 69` | ✅ High | Matches the manuscript and `study_config.yaml`. |
| `hearing_loss_cutoff_db` | `25` | ✅ High | WHO grade-1 cutoff; matches the manuscript primary definition. |

---

## What you actually have to look up (short list)

Everything else has a trustworthy default. From the **codebook that ships with
the approved data**, confirm/fill just these:

1. `tinnitus_item` — the tinnitus question variable (❓ required).
2. `occupational_noise` — the workplace-noise question variable (❓ required).
3. The **12 audiometry threshold** variable names `O_R_/O_L_<freq>` (❓ verify).
4. `invalid_threshold_codes` — the real non-response sentinels (⚠️ matters).
5. `weight` — confirm `wt_itvex` vs `wt_tot`, and apply the `/n_years` pooling divisor (⚠️).
6. `sleep_hours` and `employment` names for your specific cycles (⚠️, optional).

Paste those into `knhanes_mapping.yaml`, drop the `.sas7bdat` files under
`code/data/raw/knhanes/<cycle>/`, and the pipeline runs.
