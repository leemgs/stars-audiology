# TRIPOD+AI Checklist — STARS

Reporting checklist for the prediction-model component, following the TRIPOD+AI
statement (Collins et al., 2024). In STARS the two research risk-stratification
models (tinnitus presence; audiometric hearing loss) are **development-stage and
prespecified**: targets, predictors, and metrics are frozen before external
validation, and only a **synthetic-scaffold** run exists so far (explicitly *not*
a result). Items are marked **[Prespecified]**, **[Reported: scaffold]**, or
**[Planned: KNHANES→NHANES]** accordingly.

> Governance note: these are *research* risk-stratification models with a
> declared intended use — never screening, diagnostic, or triage devices — and a
> deterministic red-flag layer overrides model output (see `sections/ai_system.tex`,
> `tables/table_redflag.tex`, `tables/table_intended.tex`).

| # | TRIPOD+AI item | Status | Where (STARS) |
|---|----------------|--------|---------------|
| 1 | Title identifies study as developing/validating a prediction model incl. AI | ✅ | Title/subtitle (`main.tex`); `sections/abstract.tex` |
| 2 | Structured abstract | ✅ | `sections/abstract.tex` |
| 3a | Background/rationale, clinical context | ✅ | `sections/introduction.tex`; `sections/ai_system.tex` §"Motivation" |
| 3b | Study objectives | ✅ | `sections/introduction.tex` §"Aims" (Aim 2 transportability, Aim 3 AI) |
| 4 | Data sources, setting (dev + validation) | ✅ | `sections/methods.tex` §"Fixed Datasets…"/"External Validation…"; KNHANES dev, NHANES validation |
| 5 | Eligibility / participants | ✅ | Adults 40–69; `sections/methods.tex` §"Fixed Datasets…" |
| 6 | Outcome to be predicted, definition, blinding | ✅ | Tinnitus presence; hearing loss (PTA > 25 dB HL); `sections/methods.tex` §"Outcomes"/"Research-Only Prediction Models…" |
| 7 | Predictors, definition, timing, blinding | ✅ **[Prespecified]** | `tables/table_variables.tex`, `tables/table_harmonization.tex`; common transportable set vs country-specific |
| 8 | Sample size rationale | ◑ | `sections/methods.tex` §"Sample size and precision" (fixed cycles; precision framing) |
| 9 | Missing data handling | ✅ | `sections/methods.tex` §"Missing data" (MICE; same rule in both surveys for validation) |
| 10 | Predictor/outcome preprocessing; data leakage prevention | ✅ **[Prespecified]** | Frozen feature/outcome definitions; `sections/methods.tex` §"Research-Only Prediction Models…"; deterministic seeds (`sections/ai_system.tex` §"Robustness") |
| 11 | Model type / architecture and rationale | ✅ | Survey-weighted logistic baseline → gradient-boosted comparator; simpler preferred unless calibrated gain; `sections/methods.tex` |
| 12 | Model-building / predictor selection | ✅ **[Prespecified]** | Prespecified predictors; repeated stratified CV with optimism correction |
| 13 | Measures of model performance | ✅ **[Prespecified]** | `tables/table_metrics.tex` — AUROC/AUPRC, calibration-in-the-large & slope, Brier, decision-curve net benefit |
| 14 | Model updating / recalibration | ✅ **[Prespecified]** | `sections/methods.tex` §"External Validation…" — intercept-only then intercept+slope recalibration |
| 15 | Evaluation of fairness / subgroups | ✅ **[Prespecified]** | `sections/methods.tex` §"Fairness and subgroup evaluation"; `tables/table_metrics.tex` (sex, age, employment, noise, asymmetry, SES, race/ethnicity) |
| 16 | Software, code, packages, versions | ✅ | `code/` (executable pipeline); `code/requirements.txt` (pinned); `sections/ai_system.tex` §"Robustness" (run provenance) |
| 17 | Participants flow (dev + validation) | ◑ **[Planned]** | NHANES analytic N reported; full KNHANES→NHANES flow planned |
| 18 | Model specification (final model presented) | ◑ **[Planned]** | To be reported with KNHANES development (coefficients / model card) |
| 19 | Model performance (discrimination, calibration, subgroups) | ◑ **[Reported: scaffold]** | `tables/table_metrics.tex` synthetic-scaffold values (AUROC 0.64 etc.) — explicitly *not* a result; real values **[Planned]** |
| 20 | Model updating results | ◑ **[Planned]** | Recalibration results planned in external validation |
| 21 | Interpretation vs objectives | ✅ | `sections/results.tex`, `sections/discussion.tex`; SHAP caveated as descriptive |
| 22 | Limitations | ✅ | `sections/discussion.tex`; cross-sectional; SHAP instability with correlated predictors |
| 23 | Clinical use / implications / intended use | ✅ | `tables/table_intended.tex`; `sections/ai_system.tex` §"Model Roles and Prohibitions" |
| 24 | Supplementary info / registration / protocol / data & code availability | ✅ | `sections/declarations.tex` (protocol status, data/code availability); open repository |
| 25 | Funding / conflicts | ✅ | `sections/declarations.tex` |
| **AI-1** | Explainability / interpretability methods and caveats | ✅ | `sections/methods.tex`/`sections/ai_system.tex` — SHAP descriptive only; not causal/stable with correlated predictors |
| **AI-2** | Fairness across protected subgroups (first-class results) | ✅ **[Prespecified]** | `sections/methods.tex` §"Fairness…" — subgroup calibration/error gaps as primary results |
| **AI-3** | Transportability / external validation across settings | ✅ **[Prespecified]** | `sections/methods.tex` §"External Validation Across Survey Designs" (common support, case-mix standardization) |
| **AI-4** | Human oversight / role in clinical pathway | ✅ | Deterministic red-flag override; clinician-verified extraction; `sections/ai_system.tex`, `tables/table_redflag.tex` |
| **AI-5** | Reproducibility (seeds, versions, prompts) | ✅ | `sections/ai_system.tex` §"Robustness"; pinned deps, deterministic seeds, logged prompts/schema versions |
| **AI-6** | Open medical LLM use constrained + verified | ✅ | Schema-constrained extraction, clinician-verified; `sections/ai_system.tex` §"Schema-Constrained Extraction and Governance" |

**Legend:** ✅ addressed / prespecified · ◑ partial (protocol: planned or scaffold-only) · **[Prespecified]** frozen before validation · **[Reported: scaffold]** synthetic wiring check, not a result · **[Planned: KNHANES→NHANES]** to be reported.

Reference: Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L.,
Van Calster, B., … Logullo, P. (2024). TRIPOD+AI statement: Updated guidance for
reporting clinical prediction models that use regression or machine learning
methods. *BMJ, 385*, Article e078378. https://doi.org/10.1136/bmj-2023-078378
