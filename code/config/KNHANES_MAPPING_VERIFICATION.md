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

## ⚠️ VERIFIED against the real 2010–2012 `HN{yy}_ALL` files (Aug 2026)

The downloaded 공통 "기본DB" files (`hn10_all` / `hn11_all` / `hn12_all`) were
inspected directly. Result: **the exposure side is present; the outcome side is
not.**

- ✅ **Present & confirmed in the ALL files:** `BP1` (stress), `BP5` (depression),
  `age`, `sex`, `edu`, `occp`, `ho_incm`, **`wt_itvex`**, `kstrata`, `psu`, and
  the merge key `id`. A survey-weighted check gave perceived-stress prevalence
  24.3% (95% CI 23.2–25.3, n=9,751) for adults 40–69 — the exposure pipeline
  works on real data.
- ❌ **NOT in the ALL files:** tinnitus, occupational noise, and audiometry
  thresholds. The earlier `HtE_1` / `HtE_5` / `O_R_###` guesses are **disproven**
  for these files (the `O_*` columns there are the ORAL/dental exam). The KNHANES
  이비인후검사 (ENT: 순음청력 + 이명), fielded on adults ≥40, is a **separate
  file** that must be downloaded and **merged on `id`**. Those variable names are
  pending that file's codebook.

---

## Survey design

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `weight` | `wt_itvex` | ✅ Confirmed (ALL file) | `wt_itvex` (설문,검진 통합가중치) is present in all three ALL files and is correct for the interview+exam analysis. Pool with `wt_itvex/3` (see below). The audiometry outcomes are a ≥40 subsample, so the **otology-exam subsample weight (expected in the ENT file)** should be used for the hearing models once that file is supplied. |
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

## Outcomes (**not in the ALL files — pending the separate ENT file**)

These live in the KNHANES 이비인후검사 (ENT) file, **not** the `HN{yy}_ALL` files
that were downloaded. The `HtE_1` / `HtE_5` guesses are **disproven for the ALL
files** and are now `<FILL>` pending the ENT file's codebook.

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `tinnitus_item` | `<FILL>` | ❓ Pending ENT file | The "past-year tinnitus" question (the construct Park et al., 2014 used). Set from the ENT file's codebook after that file is supplied. |
| `tinnitus_yes_values` | `[1]` | ⚠️ Medium | Plausible (1 = yes) but confirm against the ENT codebook. |
| `occupational_noise` | `<FILL>` | ❓ Pending ENT file | Workplace loud-noise exposure question, in the ENT/occupational module. Set from the ENT codebook. |

## Audiometry (pure-tone thresholds)

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `500`…`6000` right/left vars | `<FILL>` | ❓ Pending ENT file | **Disproven for the ALL files** — the `O_*` columns there are the ORAL/dental exam, not audiometry. Set all 12 names from the ENT/audiometry file's codebook. |
| `invalid_threshold_codes` | `[99999, 66666]` | ⚠️ Pending ENT file | Non-response / could-not-test sentinels vary. **Confirm against the ENT codebook** — a wrong sentinel silently corrupts the PTA means. |
| `speech_freqs` | `["500","1000","2000","4000"]` | ✅ High | Standard speech-frequency PTA definition (0.5/1/2/4 kHz), consistent with the manuscript's PTA$_{0.5,1,2,4}$. |

## Files & analysis window

| Field | Default | Confidence | Note |
|-------|---------|-----------|------|
| `files.*.exam` | `hn10_all.sas7bdat`, … (lowercase) | ✅ Confirmed | The actual downloaded filenames are lowercase; mapping updated. |
| `files.*.ent` | `<FILL_ENT_20xx>` | ❓ Pending | The separate ENT/audiometry file per year — still to be downloaded; the loader will merge it on `id`. |
| **2009 cycle** | *(intentionally absent)* | ✅ High | Resolved: the study window is **2010–2012 (KNHANES V)**. The protocol text (`study_config.yaml`, `methods.tex`, `public_data.tex`, `table_harmonization.tex`) was narrowed to match the mapping/CLI, so no 2009 file is needed. |
| `age_min/max` | `40 / 69` | ✅ High | Matches the manuscript and `study_config.yaml`. |
| `hearing_loss_cutoff_db` | `25` | ✅ High | WHO grade-1 cutoff; matches the manuscript primary definition. |

---

## What you actually have to look up (short list)

The exposure/covariate side is done and verified. **Everything left comes from
the separate ENT/audiometry file** (once downloaded) and its codebook:

1. Download the **ENT/audiometry file** for 2010–2012 (see `KDCA_DATA_REQUEST_GUIDE.md`).
2. `tinnitus_item` and `occupational_noise` — the ENT questionnaire items.
3. The **12 audiometry threshold** variable names + `invalid_threshold_codes`.
4. The **otology-exam subsample weight** (the ENT models should use it, not `wt_itvex`).
5. (optional) `sleep_hours`, `employment` — mediator/covariate niceties.

Already handled in code/config: `weight: wt_itvex` (confirmed), the `/n_years`
pooling divisor plan, lowercase `exam` filenames, and the `ent:` file slots.

Paste those into `knhanes_mapping.yaml`, drop the `.sas7bdat` files under
`code/data/raw/knhanes/<cycle>/`, and the pipeline runs.
