# STROBE Checklist — STARS

Reporting checklist for observational (cross-sectional) analyses, following the
STROBE Statement (von Elm et al., 2007). STARS is a **pre-analysis protocol with
a preliminary NHANES demonstration**; items describing results are marked
**[Reported: NHANES demo]** where the preliminary analysis addresses them and
**[Planned: KNHANES]** where the item is prespecified but not yet reported.

Section/line references point to the LaTeX sources under `paper/`.

| # | STROBE item | Addressed? | Where (STARS) |
|---|-------------|-----------|---------------|
| 1a | Study design in title/abstract | ✅ | Title (`main.tex`); `sections/abstract.tex` — "pre-analysis study protocol", cross-sectional survey analyses |
| 1b | Informative, balanced abstract | ✅ | `sections/abstract.tex` (structured: Purpose/Method/Contributions/Preliminary results/Conclusions) |
| 2 | Background/rationale | ✅ | `sections/introduction.tex`; `sections/related_work.tex` |
| 3 | Objectives / prespecified hypotheses | ✅ | `sections/introduction.tex` §"Aims and hypotheses" (H1–H3, falsifiable) |
| 4 | Study design early in paper | ✅ | `sections/methods.tex` §"Study Design" (3 stages); `sections/abstract.tex` |
| 5 | Setting, locations, dates | ✅ | `sections/methods.tex` §"Fixed Datasets, Cycles, and Eligibility" — KNHANES V (2010–2012); NHANES 2011–2012/2015–2016/2017–2018; `tables/table_datasets.tex` |
| 6a | Eligibility criteria, sources, methods | ✅ | `sections/methods.tex` §"Fixed Datasets…" — adults 40–69, valid exam weights, non-missing outcome |
| 6b | Matching criteria (if applicable) | n/a | Not a matched design; survey-weighted population analysis |
| 7 | Variables: outcomes, exposures, confounders, effect modifiers | ✅ | Exposure `sections/methods.tex` §"Exposure…"; outcomes §"Outcomes"; confounders/mediators §"Causal Structure…" + `fig:dag`; `tables/table_variables.tex`, `tables/table_harmonization.tex` |
| 8 | Data sources / measurement per variable | ✅ | `tables/table_harmonization.tex` (original item, scale, harmonization rule, comparability rating); `code/config/knhanes_mapping.yaml` + `KNHANES_MAPPING_VERIFICATION.md` |
| 9 | Bias | ✅ | `sections/methods.tex` — healthy-worker/collider (all-adult primary), overadjustment (mediators separate), measurement-comparability handling; `sections/discussion.tex` (limitations) |
| 10 | Study size | ✅ | `sections/methods.tex` §"Sample size and precision" (precision framing; fixed cycles); NHANES analytic N reported (`tables/table_results.tex`) |
| 11 | Quantitative handling of variables / groupings | ✅ | Stress dichotomized (high vs low); PTA cutoffs 25 dB HL primary, 20 dB HL sensitivity; `sections/methods.tex` §"Outcomes"/"Statistical Analysis" |
| 12a | Statistical methods incl. confounding control | ✅ | `sections/methods.tex` §"Statistical Analysis" — survey-weighted (Taylor linearization), minimal sufficient adjustment set |
| 12b | Subgroups and interactions | ✅ | `sections/methods.tex` §"Fairness and subgroup evaluation"; `sections/methods.tex` §"Sensitivity Analyses" |
| 12c | Missing data | ✅ | `sections/methods.tex` §"Missing data" — MICE (MAR), complete-case sensitivity |
| 12d | Sampling strategy accounting | ✅ | Survey design honored (weight/strata/PSU); `code/src/nhanes_analysis.py`, `code/src/knhanes_analysis.py` |
| 12e | Sensitivity analyses | ✅ | `sections/methods.tex` §"Sensitivity Analyses" |
| 13 | Participants (numbers at each stage) | ◑ | **[Reported: NHANES demo]** analytic N per outcome (`tables/table_results.tex`, `code/outputs/nhanes_results.json`). **[Planned: KNHANES]** full flow to be reported |
| 14 | Descriptive data / characteristics / missingness | ◑ | **[Reported: NHANES demo]** weighted prevalences; **[Planned: KNHANES]** full descriptive table |
| 15 | Outcome events / summary measures | ◑ | **[Reported: NHANES demo]** `tables/table_results.tex`; **[Planned: KNHANES]** `tab:results_knhanes` |
| 16a | Unadjusted + adjusted estimates + CIs | ◑ | **[Reported: NHANES demo]** adjusted design-based ORs with 95% CIs (`tables/table_results.tex`); **[Planned: KNHANES]** primary perceived-stress models |
| 16b | Category boundaries reported | ✅ | Age band 40–69; PTA cutoffs; stress high={1,2}; `code/config/*` |
| 16c | Relative → absolute risk (if relevant) | ◑ | Weighted prevalences reported; absolute translation planned where relevant |
| 17 | Other analyses (subgroups, sensitivity) | ◑ | **[Planned]** `sections/methods.tex` §"Fairness…"/"Sensitivity Analyses" |
| 18 | Key results w.r.t. objectives | ✅ | `sections/results.tex` §"Interpretation (a priori pattern)"; `sections/discussion.tex` |
| 19 | Limitations | ✅ | `sections/discussion.tex`; abstract/results caveats ("associations, not causal effects") |
| 20 | Interpretation (cautious, causal caveats) | ✅ | Throughout — strict "perceived stress" naming, no causal claims; `sections/introduction.tex` §"Conservative premise", `sections/discussion.tex` |
| 21 | Generalizability | ✅ | `sections/methods.tex` §"External Validation…"; `sections/discussion.tex` (cross-national transportability) |
| 22 | Funding | ✅ | `sections/declarations.tex` §"Funding" |

**Legend:** ✅ addressed · ◑ partially (protocol: planned for KNHANES / demonstrated on NHANES) · n/a not applicable.

Reference: von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C.,
& Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational
Studies in Epidemiology (STROBE) statement. *Annals of Internal Medicine,
147*(8), 573–577. https://doi.org/10.7326/0003-4819-147-8-200710160-00010
