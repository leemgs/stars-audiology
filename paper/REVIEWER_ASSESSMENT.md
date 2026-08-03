# STARS — Reviewer-Perspective Assessment (target: *American Journal of Audiology*)

A candid pre-submission review written as an AJA reviewer (audiologist /
otolaryngologist / hearing scientist) would see it, now that the primary KNHANES
result is reported. Items are prioritized: **Major** (likely to drive a
major-revision or reject decision if unaddressed), **Moderate**, **Minor**.
Section references point to `paper/sections/`.

The goal is acceptance-readiness, so the tone is deliberately critical. There is
a genuinely strong paper here; most items are about *bounding the claim* and
*focusing the contribution*.

---

## What is already strong (keep and foreground)

- A **prespecified, falsifiable hypothesis (H1)** with a real, coherent result:
  perceived stress tracks the tinnitus *symptom* (OR 1.42) but attenuates against
  the audiometric *threshold* (OR 1.18, ns). The symptom-vs-threshold framing is
  the paper's best idea — make it the spine.
- **Reproducibility** most audiology papers lack: committed code, mapping, and
  `knhanes_results.json` that regenerates every number. Reviewers reward this.
- Disciplined **non-causal language** and DAG-based adjustment reasoning.
- Two-cohort (KNHANES primary + NHANES supporting) directional consistency.

---

## Major concerns

### M1. Cross-sectional design → reverse causation is the elephant
The single most predictable reviewer objection: **tinnitus causes distress at
least as plausibly as stress "causes" tinnitus.** Bothersome tinnitus is itself
a stressor. A cross-sectional OR of 1.42 cannot separate the two directions.
- *Fix:* address reverse causation head-on in the Discussion (not just "cross-
  sectional" in a limitations list). State the directionality threat explicitly,
  note that the design cannot resolve it, and soften any language that implies
  stress precedes tinnitus. Consider a sensitivity analysis restricted to
  *non-bothersome* tinnitus (weaker feedback loop) — if the stress association
  persists there, it partially blunts the reverse-causation critique.

### M2. Under-adjustment of the primary model — bring the extended models INTO the paper
The primary tinnitus model adjusts only for noise, age, sex (Results). Reviewers
will immediately ask:
- **Hearing loss is not in the tinnitus model.** Hearing loss is one of the
  strongest tinnitus correlates; a reviewer will want to see whether
  stress→tinnitus survives adjustment for audiometric hearing loss (treating it
  per your DAG as confounder or common cause).
- **Depression (BP5) is a DAG mediator but its extended-model result is only "in
  the repository."** Depression is powerfully linked to both stress and tinnitus;
  reviewers will want the mediator-adjusted estimate *in the paper* to judge how
  much of the 1.42 is independent of mood.
- Cardiometabolic factors, smoking, and SES are available in KNHANES and are
  conventional covariates in this literature.
- *Fix:* add a second results column/table showing the **extended
  (mediator/comorbidity-adjusted)** model and the **hearing-loss-adjusted**
  tinnitus model. "Reported in the extended repository outputs" (current Results
  wording) will read as evasive to a reviewer — the key sensitivity analyses
  belong in the manuscript.

### M3. Measurement validity — single-item exposure and outcome
- **Perceived stress = one general item (`BP1`)**, not a validated instrument
  (PSS-10, Effort–Reward Imbalance, JCQ). The manuscript is honest about this,
  but a reviewer will weight it heavily because it is *the exposure*.
- **Tinnitus = one self-report item**; no validated tinnitus measure (THI/TFI),
  and no audiometric tinnitus confirmation.
- *Fix:* elevate these from the limitations list to a short "Measurement" note,
  quantify the expected direction of bias (non-differential misclassification →
  attenuation, so the true tinnitus association may be larger), and temper claims
  accordingly. Do not overstate "perceived stress" beyond a single item.

### M4. Scope / article identity — the paper is trying to be four papers
It is simultaneously (a) a pre-analysis protocol, (b) an empirical KNHANES study,
(c) an open-AI/MedGemma extraction architecture, and (d) a deterministic SSNHL
red-flag safety-engineering paper. For AJA this reads as unfocused, and the
**AI/safety component is entirely prospective (no results)** — a reviewer may
call it padding or "salami with itself."
- *Fix (recommended):* refocus the submission around the empirical
  symptom-vs-threshold finding + the reproducible cross-national scaffold. Move
  the LLM-extraction and red-flag-layer architecture to a **companion methods/
  perspective paper** (or a clearly-scoped short section), and confirm with the
  editor which article type this is. Decide: is this a Research Article (lead with
  results) or a Registered-Report-style protocol? Right now it is both, and the
  hybrid framing (see Minor m2) confuses the reader.

### M5. Novelty vs. prior KNHANES tinnitus–stress literature
KNHANES 2010–2012 has already been mined for tinnitus and its psychological
correlates (e.g., mental-health/BMI–tinnitus analyses in this exact cycle range,
and Park et al. 2014 on tinnitus prevalence/associated factors). A reviewer who
knows this literature will ask **"what is new?"**
- *Fix:* add a paragraph in Related Work that names the closest prior KNHANES
  stress/mental-health–tinnitus studies and states precisely what STARS adds
  (the prespecified symptom-vs-threshold contrast, the DAG-based
  mediator-vs-confounder separation, the cross-national KNHANES→NHANES
  consistency, and the reproducible scaffold). Novelty must be explicit, not
  implied.

### M6. Survey-variance / estimation details a statistician reviewer will probe
Inspecting the estimators (`code/src/nhanes_analysis.py`):
- **Subpopulation (domain) estimation:** the 40–69 analytic set is created by
  *subsetting the data* before variance estimation (`run_analysis` filters, then
  `svy_mean`/`svy_logistic` linearize on the subset). Correct practice is
  **domain/subpopulation estimation that retains the full design**; subsetting can
  distort the stratum/PSU structure and the SEs.
- **Single-PSU strata contribute 0 variance** (`if n_h < 2: continue`), described
  as "conservative" — but dropping a stratum's term generally **under**estimates
  variance (anti-conservative, CIs too narrow). After subsetting + complete-case
  this can bite, and it matters for the borderline hearing-loss result
  (p = 0.066).
- **Complete-case vs. planned MICE:** Methods prespecify multiple imputation
  (MICE) as primary, but the reported analysis is complete-case (`dropna`). This
  is a plan-vs-execution mismatch reviewers will flag.
- *Fix:* reproduce the headline estimates in an established survey package (R
  `survey` with `svydesign(...)` + `subset()` domain estimation, or Python
  `samplics`), report those SEs/CIs, handle single-PSU strata by the standard
  centering option, and reconcile the missing-data method (either run MICE or
  change Methods to state complete-case primary with MICE as sensitivity).

---

## Moderate concerns

### Mo1. Audiometric outcome definition
- Better-ear PTA at 0.5/1/2/4 kHz is a reasonable primary, but it **masks
  unilateral/asymmetric loss** (the presentation most relevant to the SSNHL
  motivation) and **omits the high frequencies (3/4/6 kHz) where noise damage
  shows first.** The worse-ear and high-frequency analyses are prespecified but,
  again, only "in the repository."
- Clarify KNHANES ENT audiometry specifics reviewers will ask about:
  **air-conduction only?** Was **tympanometry / bone conduction** available to
  exclude conductive loss (Methods imply "where tympanometry permits")? If the
  KNHANES ENT exam lacked it, say so and treat conductive contamination as a
  limitation.
- *Fix:* bring worse-ear and high-frequency PTA results into the paper (at least
  a supplementary table referenced in text), and state the audiometric protocol
  and conductive-exclusion status explicitly.

### Mo2. Survey weight for the ENT sub-sample
The audiometry/tinnitus outcomes come from the ≥40 ENT sub-sample, analyzed with
the distributed interview+exam weight (`wt_itvex`) because KDCA released no
ENT-specific weight. A survey-methods reviewer may question whether `wt_itvex` is
correctly calibrated to the ENT sub-sample.
- *Fix:* state this explicitly (already noted in Discussion), and confirm against
  the KNHANES 이용지침서 whether an otology-exam weight exists for these cycles; if
  not, justify `wt_itvex` and flag residual weighting uncertainty.

### Mo3. Clinical relevance and the vignette↔finding gap
The motivating vignette is about **SSNHL urgency (the golden window)**, but the
empirical finding is a **cross-sectional stress–tinnitus association.** These are
only loosely connected, and an AJA reviewer will ask "so what should the clinician
do?"
- *Fix:* add a concrete clinical-implications paragraph tying the finding to
  audiology practice (e.g., stress/tinnitus counseling, not attributing acute
  asymmetric loss to stress), and make explicit that the SSNHL safety layer is a
  *separate, prospective* contribution rather than a conclusion of the data.

### Mo4. NHANES as "support" is a different construct
NHANES uses a PHQ-9 depression proxy (a DAG *mediator*), not perceived stress, so
it does not truly *externally validate* the stress exposure. The manuscript is
careful, but reviewers may still discount it.
- *Fix:* frame NHANES explicitly as "directional consistency of the
  symptom-vs-threshold pattern under a related but distinct distress construct,"
  not as validation of the stress effect.

### Mo5. Age ceiling at 69
Capping at 69 excludes the ≥70 group with the highest tinnitus/hearing burden.
The rationale (ENT exam ≥40; mid/late-career) is defensible but should be stated
as a generalizability limit, with a note on how estimates might differ in elders.

---

## Minor concerns

- **m1. Abstract length.** Now ~250–300+ words with the new results; confirm the
  AJA limit (often ~250) and trim.
- **m2. Consistent framing.** Several passages still call it "a protocol, not a
  results paper" in spirit while the abstract/Results now lead with primary
  findings. Make the identity consistent throughout (see M4).
- **m3. "In the repository" over-reliance.** Reviewers cannot condition
  acceptance on un-shown analyses; move the key ones (extended model, worse-ear,
  employed-restricted) into the manuscript or a supplement that is submitted.
- **m4. Effect-size interpretation.** Add a sentence on the clinical
  meaning/magnitude of OR 1.42 (and whether a marginal OR 1.18 at p=0.066 should
  be called "null" vs. "weak/attenuated" — prefer the latter, and avoid
  dichotomizing around p=0.05).
- **m5. Multiplicity.** Several endpoints/associations are reported; state the
  primary vs. secondary hypotheses and the FDR/adjustment plan (Methods mention
  it — make sure the reported results reflect it).
- **m6. STROBE/TRIPOD+AI checklists** exist in `paper/checklists/` — cite them
  explicitly and submit them as supplements.
- **m7. Bothersome tinnitus definition** is now codebook-confirmed (moderate+
  severe annoyance) — good; state the definition inline where it is first used.

---

## Suggested revision order (highest leverage first)

1. **Refocus** the article (M4) and confirm article type with the editor.
2. **Bring the extended / hearing-loss-adjusted / worse-ear analyses into the
   paper** (M2, Mo1) — this is the biggest credibility gain.
3. **Reproduce SEs in an established survey package** and reconcile MICE vs
   complete-case (M6).
4. **Reframe causality and measurement** limits as first-class (M1, M3), with a
   non-bothersome-tinnitus sensitivity analysis.
5. **Sharpen novelty** against prior KNHANES work (M5) and the **clinical
   implications** (Mo3).
6. Minor polish (abstract length, framing consistency, effect-size language).
