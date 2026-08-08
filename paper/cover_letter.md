# Cover Letter (Draft)

> Draft for the STARS submission to the *American Journal of Audiology* (AJA).
> Placeholders in **[brackets]** must be completed before submission (the date;
> optionally the editor's name). This is a working draft, not a final letter.

---

**[Date]**

To the Editor-in-Chief
*American Journal of Audiology* (AJA)
American Speech-Language-Hearing Association

**Re: Submission of “Perceived Stress Tracks the Tinnitus Symptom More Than the Audiometric Threshold: A Survey-Weighted KNHANES Study (STARS).”**

Dear Editor,

I am pleased to submit my manuscript, **STARS** (**S**tress, **T**innitus, and **A**udiometric **R**esearch **S**tudy), for consideration in the *American Journal of Audiology*. I propose it as a **Research Article (survey-weighted public-data analysis) reported against a prespecified analysis plan**, and I would welcome your guidance on the most appropriate article category.

**What the manuscript is.** STARS reports a survey-weighted, reproducible analysis of the associations among perceived stress, tinnitus, and hearing outcomes in adults, built around one primary finding and a prespecified plan for prospective follow-on components. To guard against analyst degrees of freedom, the design—survey cycles, age windows, endpoints, a causal DAG with a minimal sufficient adjustment set, and all metrics—was fixed before analysis, and it is accompanied by fully open, reproducible code that regenerates every number.

**Primary finding (real KNHANES data).** In the Korea National Health and Nutrition Examination Survey (adults 40–69; otologic cycles 2010–2012)—which, unlike NHANES, carries a general perceived-stress item—high perceived stress was associated with **tinnitus** (OR 1.42, 95% CI 1.26–1.60, *p* < 0.001) but only weakly and non-significantly with the **audiometric threshold** (OR 1.18, 0.99–1.41, *p* = 0.07), which was instead dominated by occupational noise and age. This prespecified **symptom-versus-threshold dissociation** (hypothesis H1) is the manuscript’s central contribution. In supporting U.S. NHANES analyses, the same directional pattern recurred under a PHQ-9 distress proxy—directional consistency, not external validation of the stress exposure. I am explicit that all estimates are cross-sectional associations, that reverse causation (tinnitus→stress) cannot be excluded, and that the single-item exposure biases associations toward the null.

**Why it fits AJA and why it matters clinically.** The work is deliberately audiology-centered: it separates tinnitus presence from bothersome tinnitus and analyzes better-ear, worse-ear, and high-frequency thresholds rather than a single better-ear summary. Clinically, it supports incorporating stress into counseling for stable tinnitus while cautioning against attributing acute or asymmetric hearing loss to “stress.” A deterministic “red-flag” referral layer for sudden sensorineural hearing loss (SSNHL) is presented as a **prospective** safety-engineering component (design only), so a low predicted risk can never suppress urgent evaluation.

**Contributions.**
1. A prespecified, reproducible survey-weighted result dissociating the tinnitus **symptom** from the audiometric **threshold** for perceived stress, without unsupported causal claims.
2. An open, reproducible scaffold—harmonized variable mappings, unit-tested design-based estimators (with domain estimation and conservative single-PSU handling), model cards, and safety tests—so others can regenerate every number and add local cohorts.
3. *(Prospective, design only)* a KNHANES→NHANES external-validation plan (calibration, recalibration, common support, subgroup fairness) and a clinician-governed AI-extraction plus deterministic red-flag referral-safety component.

**Rigor and reporting.** The observational analyses follow STROBE and the prediction models follow TRIPOD+AI; the planned clinical extension will follow SPIRIT. All code, configuration, tables, and a synthetic-data path are openly available at <https://github.com/leemgs/stars-audiology>.

**Responsible-AI statement.** Any prediction model in STARS is a research risk-stratification tool with a declared intended use—never a screening, diagnostic, or triage device—and open medical language models are confined to clinician-verified research extraction. Generative AI tools assisted in drafting; the author reviewed and takes full responsibility for all content.

**Declarations.** This manuscript is original, is not under consideration elsewhere, and has not been published previously. The author has approved the submission and agrees to be accountable for the work. The analyses use fully deidentified, publicly available survey data; any prospective clinical extension will proceed only under institutional review board approval. The author declares no competing interests. No external funding supported this work.

I believe STARS offers AJA readers a transparent, reproducible, and clinically safe template for studying stress-related auditory outcomes, and I thank you for considering it.

Sincerely,

**Geunsik Lim** (sole and corresponding author) — Sungkyunkwan University, Republic of Korea — leemgs@g.skku.edu — ORCID [0000-0003-1845-7132](https://orcid.org/0000-0003-1845-7132)

---

*Suggested reviewers and any preferred/non-preferred reviewers can be added here per AJA policy.*
