# TRIPOD+AI Checklist — SAFE-EAR (companion paper B)

Reporting checklist for the AI/extraction + deterministic-safety component,
following the TRIPOD+AI statement (Collins et al., 2024). This checklist covers
the **realized** content of the SAFE-EAR paper (`../main.tex`): a deterministic,
guideline-derived red-flag safety layer over schema-constrained clinical-text
extraction, evaluated on an open 71-case benchmark with two reproducible
rule-based extractors.

> **Scope note.** The two research *risk-stratification prediction models*
> (tinnitus presence; audiometric hearing loss, with AUROC/AUPRC/calibration)
> that appeared in the original combined protocol are **prospective** and are not
> reported in either the empirical STARS paper (`../../paper/`, STROBE) or this
> benchmark paper; the corresponding rows below are marked **[Prospective]**.
> The **realized** subject here is the deterministic red-flag layer + rule-based
> extraction benchmark, whose evaluation plan is prespecified and whose metrics
> are computed on an open, no-patient-data benchmark.

> **Governance.** The extractor is a *research* tool with a declared intended
> use — never a screening, diagnostic, or triage device. A deterministic
> red-flag layer overrides any probabilistic output and cannot be suppressed by a
> low predicted risk, and extracted red-flag features are clinician-verified
> before use (`../main.tex` §"System architecture", §"Governance").

| # | TRIPOD+AI item | Status | Where (SAFE-EAR / paper02) |
|---|----------------|--------|---------------|
| 1 | Title identifies study as developing/evaluating an AI-assisted method | ✅ | Title/subtitle (`../main.tex`) |
| 2 | Structured abstract | ✅ | `../main.tex` (Objective / Materials and Methods / Results / Discussion / Conclusion) |
| 3a | Background/rationale, clinical context | ✅ | `../main.tex` §"Background and Significance" |
| 3b | Study objectives | ✅ | `../main.tex` §"Background and Significance" (Contributions); abstract Objective |
| 4 | Data sources, setting | ✅ | Open benchmark, expert-authored/synthetic, **no patient data**; `../main.tex` §"Open benchmark" |
| 5 | Eligibility / case construction | ✅ | 71 cases (34 structured, 37 free-text) across four note categories; `../main.tex` §"Open benchmark" |
| 6 | Outcome to be predicted, definition | ✅ | Guideline-defined red-flag urgency (SSNHL/tinnitus CPGs); gold assigned a priori, independent of rule code; `../main.tex` §"Guideline-derived red-flag rules" |
| 7 | Predictors (extracted features), definition, timing | ✅ | Typed fields + boolean red-flag features from schema-constrained extraction; `../main.tex` §"Reproducible extraction baseline"; `../tables/table_extraction.tex` |
| 8 | Sample size rationale | ◑ | Curated 71-case benchmark; Wilson 95% CIs reported; harness supports arbitrary N; `../main.tex` §"Limitations" |
| 9 | Missing data handling | ✅ | Complete synthetic cases; extractor handles absent/implicit cues (colloquial/ambiguous categories); `../main.tex` §"Reproducible extraction baseline" |
| 10 | Preprocessing; leakage prevention | ✅ | Deterministic rule-based extraction; gold urgency assigned **independently** of the rule code; `../main.tex` §"Two-level evaluation" |
| 11 | Model type / architecture and rationale | ✅ | Deterministic rule layer over a schema-constrained extractor (extraction → non-overridable safety floor); `../main.tex` §"System architecture" |
| 12 | Model-building / rule selection | ✅ **[Prespecified]** | Seven red-flag rules derived from the SSNHL and tinnitus clinical practice guidelines; `../main.tex` §"Guideline-derived red-flag rules" |
| 13 | Measures of performance | ✅ **[Prespecified]** | Red-flag recall (Wilson 95% CI), specificity, over-referral, per-field precision/recall/F1, urgency-changing error rate, run-to-run consistency; `../main.tex` §"Two-level evaluation" |
| 14 | Model updating / recalibration | n/a | Deterministic layer has no fitted parameters; the extractor improvement (v1→v2) is documented instead; `../main.tex` §"Reproducible extraction baseline" |
| 15 | Evaluation of fairness / subgroups | ✅ | Per-note-category performance (typical, negation, colloquial, ambiguous); `../tables/table_redflag_bycat.tex` |
| 16 | Software, code, packages, versions | ✅ | `../../code/src/redflag_benchmark.py`, `safety.py`, `run_redflag_eval.py`, `run_extraction_eval.py`; `../../code/requirements.txt` (pinned) |
| 17 | Participant flow | ✅ | 34 structured (19 urgent / 15 benign) + 37 free-text (18 urgent / 19 benign); `../main.tex` §"Open benchmark" |
| 18 | Model specification (final rules presented) | ✅ | Seven rules fully specified and deterministic/auditable; `../main.tex` §"Guideline-derived red-flag rules" |
| 19 | Performance results (discrimination, subgroups) | ✅ | Rule coverage 100% recall / 0% over-referral; end-to-end recall 56%→100% across extractors; `../main.tex` §"Results"; `../tables/table_redflag_results.tex`, `../tables/table_extraction_compare.tex`, `../tables/table_extraction.tex` |
| 20 | Model updating results | ✅ | Extractor v1 (56% recall) → v2 (100%) on the benchmark; macro-F1 0.72→0.94; `../main.tex` §"Results" |
| 21 | Interpretation vs objectives | ✅ | `../main.tex` §"Discussion" |
| 22 | Limitations | ✅ | `../main.tex` §"Limitations"; finite-set 100% is a target, not a deployment guarantee |
| 23 | Clinical use / implications / intended use | ✅ | Research tool only; deterministic override + mandatory clinician verification; `../main.tex` §"Governance", §"Discussion" |
| 24 | Supplementary info / registration / data & code availability | ✅ | `../main.tex` §"Declarations"; open benchmark, rules, extractors, and metrics released |
| 25 | Funding / conflicts | ✅ | `../main.tex` §"Declarations" |
| **AI-1** | Explainability / interpretability methods and caveats | ✅ | Deterministic, fully auditable rules (inherently interpretable); `../main.tex` §"Governance" |
| **AI-2** | Fairness across subgroups (first-class results) | ✅ | Per-category red-flag recall reported as a primary result; `../tables/table_redflag_bycat.tex` |
| **AI-3** | Transportability / external validation across settings | ◑ **[Prospective]** | Real-note and multilingual robustness remain to be tested; `../main.tex` §"Limitations" |
| **AI-4** | Human oversight / role in clinical pathway | ✅ | Non-overridable deterministic red-flag layer + clinician-verified extraction; `../main.tex` §"System architecture", §"Governance", §"Discussion" |
| **AI-5** | Reproducibility (seeds, versions, determinism) | ✅ | Run-to-run consistency 1.00; deterministic rules/extractors; open harness; `../main.tex` §"Results", §"Declarations" |
| **AI-6** | Open medical LLM use constrained + verified | ✅ **[Prospective for the LLM step]** | Schema-constrained extraction; MedGemma evaluation is prospective via the same fixed harness/adapter; `../main.tex` §"System architecture", §"Reproducible extraction baseline" |
| — | Risk-stratification prediction models (tinnitus / hearing loss; AUROC/AUPRC, calibration, decision-curve) | **[Prospective]** | Not reported in either paper; prospective component of the STARS program |

**Legend:** ✅ addressed / prespecified · ◑ partial · n/a not applicable (deterministic, no fitted parameters) · **[Prespecified]** frozen before evaluation · **[Prospective]** planned, not reported here.

Reference: Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L.,
Van Calster, B., … Logullo, P. (2024). TRIPOD+AI statement: Updated guidance for
reporting clinical prediction models that use regression or machine learning
methods. *BMJ, 385*, Article e078378. https://doi.org/10.1136/bmj-2023-078378
