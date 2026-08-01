# Cover Letter (Draft)

> Draft for the STARS submission to the *American Journal of Audiology* (AJA).
> Placeholders in **[brackets]** must be completed before submission (ORCID,
> dates, editor name). This is a working draft, not a final letter.

---

**[Date]**

To the Editor-in-Chief
*American Journal of Audiology* (AJA)
American Speech-Language-Hearing Association

**Re: Submission of “STARS: A Pre-Analysis Protocol for Public-Data Studies of Perceived Stress, Work-Related Factors, Tinnitus, and Hearing Outcomes.”**

Dear Editor,

We are pleased to submit our manuscript, **STARS** (**S**tress, **T**innitus, and **A**udiometric **R**esearch **S**tudy), for consideration in the *American Journal of Audiology*. We propose it as a **Study Protocol / Pre-Analysis Plan with a preliminary empirical demonstration**; we would welcome your guidance on the most appropriate article category.

**What the manuscript is.** STARS prespecifies a survey-weighted, public-data investigation of the associations among perceived stress / work-related factors, tinnitus, and hearing outcomes in adults, together with a cross-national external-validation plan and a clinician-governed, safety-gated AI architecture. The design—survey cycles, age windows, endpoints, a causal DAG with a minimal sufficient adjustment set, and all evaluation metrics—is fixed in advance to guard against analyst degrees of freedom, and is accompanied by fully open, reproducible code.

**Why it fits AJA and why it matters clinically.** The work is deliberately audiology-centered: it separates tinnitus presence from bothersome tinnitus, analyzes better-, worse-ear, and per-ear thresholds rather than a single better-ear summary, and—most consequentially—embeds a deterministic “red-flag” referral layer so that a low predicted risk can never suppress urgent evaluation of sudden sensorineural hearing loss (SSNHL). This operationalizes the clinical “golden window” for SSNHL as a software guarantee, a point of direct relevance to audiologists and otolaryngologists.

**Preliminary results (real data).** As a proof of concept, we report a preliminary analysis of real U.S. NHANES public-use data (adults 40–69; pooled 2011–2018). Survey-weighted prevalence was 28.5% (95% CI 26.5–30.4) for tinnitus and 12.0% (10.4–13.6) for better-ear hearing loss. In mutually adjusted, design-based models, tinnitus was associated with occupational noise (OR 1.59) and a depression-screen distress proxy (OR 1.61), whereas hearing loss was dominated by age (OR 1.11/year) and the distress proxy (OR 2.29), with only a weak, non-significant noise association—a symptom-versus-threshold dissociation consistent with our a-priori hypotheses. We are explicit that these are cross-sectional associations, that NHANES lacks a validated perceived-stress instrument (so the exposure here is a mediator-level distress proxy), and that the **primary** perceived-stress analysis is reserved for KNHANES, for which a mapping-driven pipeline is implemented and ready.

**Contributions.**
1. A survey-weighted public-data framework that distinguishes stress–tinnitus from stress–audiometric-threshold associations without unsupported causal claims.
2. A prespecified KNHANES→NHANES external-validation plan reporting calibration, recalibration, common support, clinical utility, and subgroup fairness.
3. A clinically governed AI architecture in which schema-constrained language-model extraction is clinician-verified and a deterministic red-flag layer overrides probabilistic predictions for time-critical hearing symptoms.
4. An open, reproducible scaffold—harmonized variable mappings, executable code, model cards, safety tests, and a synthetic-data pathway—so others can reproduce and extend the analyses.

**Rigor and reporting.** The observational analyses follow STROBE and the prediction models follow TRIPOD+AI; the planned clinical extension will follow SPIRIT. All code, configuration, tables, and a synthetic-data path are openly available at <https://github.com/leemgs/stress-ear-ai>.

**Responsible-AI statement.** Any prediction model in STARS is a research risk-stratification tool with a declared intended use—never a screening, diagnostic, or triage device—and open medical language models are confined to clinician-verified research extraction. Generative AI tools assisted in drafting; the authors reviewed and take full responsibility for all content.

**Declarations.** This manuscript is original, is not under consideration elsewhere, and has not been published previously. All authors have approved the submission and agree to be accountable for the work. The preliminary analyses use fully deidentified, publicly available survey data; the prospective clinical extension will proceed only under institutional review board approval at Ajou University Hospital. The authors declare no competing interests. No external funding supported this work.

We believe STARS offers AJA readers a transparent, reproducible, and clinically safe template for studying stress-related auditory outcomes, and we thank you for considering it.

Sincerely,

**Geunsik Lim** (corresponding author) — Sungkyunkwan University, Republic of Korea — leemgs@g.skku.edu — ORCID **[to be added]**
**Hyun Jo** — Ajou University School of Medicine, Republic of Korea — joehyun@ajou.ac.kr — ORCID **[to be added]**

---

*Suggested reviewers and any preferred/non-preferred reviewers can be added here per AJA policy.*
