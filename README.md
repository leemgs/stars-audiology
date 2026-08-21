<p align="center">
  <img src="./stars-audiology.png" alt="STARS — Stress, Tinnitus, and Audiometric Research Study" width="100%">
</p>

# STARS

**STARS** = **S**tress, **T**innitus, and **A**udiometric **R**esearch **S**tudy.

This repository holds **two companion manuscripts** and the shared, reproducible
code behind them. One is an empirical epidemiology study; the other is a
patient-safety engineering study for LLM-assisted otology triage. Together they
answer *"why the problem matters"* (Paper A) and *"how to make the AI-assisted
pipeline safe"* (Paper B).

Repository: <https://github.com/leemgs/stars-audiology>

---

## Paper A — STARS (`paper/`, → *American Journal of Audiology*)

### Core idea
In a nationally representative Korean sample (KNHANES, adults 40–69), **perceived
stress was associated more strongly with the tinnitus _symptom_ than with
better-ear hearing loss** after adjustment for occupational noise, age, and sex.
This is a **symptom-vs-threshold contrast of degree**, not evidence that stress is
unrelated to hearing thresholds: the primary hearing-loss estimate was weak and
imprecise, and it strengthened after excluding middle-ear pathology.

### Core contributions
1. **A prespecified, survey-weighted, reproducible result** — stress ↔ tinnitus
   **OR 1.42** (95% CI 1.26–1.60, *p*<0.001) vs. stress ↔ better-ear hearing loss
   **OR 1.18** (0.99–1.41, *p*=0.07 after adjustment); after excluding middle-ear
   pathology using bilateral tympanometry, the hearing-loss estimate was
   **OR 1.29** (1.07–1.55). NHANES gives directional consistency under a distinct
   distress proxy, not external validation of perceived stress.
2. **An open, reproducible analysis scaffold** — harmonized variable mappings,
   design-based estimators (domain estimation, conservative single-PSU handling),
   model cards, and a synthetic-data path, so every number can be regenerated.
3. **A prespecified prospective cross-national validation plan** that is clearly
   separated from the completed analyses. The clinician-governed extraction and
   referral-safety evaluation is reported independently, with results, in Paper B.

> **What Paper A does _not_ claim.** It is **cross-sectional**, so it reports an
> **association, not causation**, and does **not** show that stress *causes* or
> that stress management *prevents* tinnitus (reverse causation — bothersome
> tinnitus raising stress — cannot be excluded). Clinically it supports
> *considering* stress when counseling patients with **stable** tinnitus, while
> **cautioning against attributing acute or asymmetric hearing loss to "stress"** —
> which is exactly the danger Paper B guards against. Because stress and tinnitus
> were measured with single self-report items, measurement error may bias the
> estimate in either direction; OR 1.42 is not presented as a lower bound.

### Submission-ready artifacts

- `paper/main.tex` contains the focused AJA Research Article and a structured
  abstract of approximately 240 words with six keywords.
- `paper/title_page.tex` is the non-anonymized title page; the `\ifblind` toggle
  in `paper/main.tex` suppresses author, affiliation, contribution, and repository
  identifiers for masked review.
- `paper/cover_letter.md` has the submission date and ORCID filled in, while
  `paper/SUBMISSION_CHECKLIST.md` records the remaining portal/editorial actions.
- `paper/supplement.tex` and `paper/checklists/` contain the supplementary methods
  and reporting checklists intended for upload with the manuscript.

---

## Paper B — SAFE-EAR (`paper02/`, → *Journal of the American Medical Informatics Association*, JAMIA)

### Core idea
When an LLM assists otology documentation/triage, a low model score must **never**
suppress referral for a time-critical emergency such as **sudden sensorineural
hearing loss (SSNHL)**. The safe design is not a better classifier but a
**non-overridable floor**: a **deterministic, guideline-derived red-flag layer**
placed *last* that overrides any probabilistic output. Crucially, the paper then
measures — honestly — that **end-to-end safety is bounded by the _extraction_
step, not the rule layer**.

### Core contributions
1. **A deterministic red-flag safety layer** (7 rules from the SSNHL and tinnitus
   guidelines) that overrides model output; on correctly-extracted features it has
   **100% rule coverage** (recall 19/19, 0% over-referral) — a guarantee achieved
   without a model.
2. **An open 71-case benchmark + two-level evaluation** (34 structured, 37
   free-text; **no patient data**) that separates *rule coverage* from *end-to-end*
   performance, isolating where risk actually arises.
3. **A real open-medical-LLM (MedGemma) result that resolves the circularity
   concern.** Scored through the *same* harness/adapter as the rule-based
   references, end-to-end red-flag recall spans **naive 56% → MedGemma-4b-it 78%
   (14/18; specificity 100%) → tuned 100%** on identical cases. Because MedGemma
   never authored the benchmark nor saw its cue lists, **78% is an
   extractor-independent measurement** — evidence the benchmark is neither
   saturated (a capable open medical LLM still misses 4/18) nor gamed (the tuned
   100% reflects benchmark-specific tuning). The honest off-the-shelf expectation
   (~78%) is why **mandatory clinician verification is load-bearing**.
4. **Fully reproducible open release** — rules, benchmark, schema-to-feature
   adapter, metrics, the MedGemma runner, and a **free-GPU notebook** that
   reproduces the MedGemma row.

---

## Paper A vs. Paper B at a glance

| | **Paper A — STARS** | **Paper B — SAFE-EAR** |
|---|---|---|
| **Question** | Is perceived stress associated with the tinnitus *symptom* vs. the audiometric *threshold*? | Can a deterministic safety layer keep LLM-assisted otology triage safe, and what bounds it? |
| **Type** | Empirical epidemiology (observational, cross-sectional) | Patient-safety engineering + open benchmark (methods) |
| **Data** | Real public survey microdata (KNHANES/NHANES, adults 40–69) | 71-case referral benchmark, expert-authored/synthetic — **no patient data** |
| **Method** | Survey-weighted, design-based regression | Guideline-derived deterministic red-flag rules + extraction + one evaluation harness |
| **Headline result** | Stress → **tinnitus OR 1.42** vs. **better-ear hearing loss OR 1.18**: a contrast of degree, with the threshold result sensitive to middle-ear exclusion | Rule coverage **100%**; end-to-end recall **naive 56% → MedGemma 78% → tuned 100%** → **extraction is the safety bottleneck** |
| **Role of AI** | None in the empirical result; prospective cross-national validation is separated from completed analyses | AI/LLM extraction **is the subject**; a real MedGemma eval is executed and **addresses benchmark circularity** |
| **Claim discipline** | Association, **not** causation or prevention | A finite-set 100% is a *target*, not a deployment guarantee |
| **Target venue** | *American Journal of Audiology* (SCIE) | *Journal of the American Medical Informatics Association*, JAMIA (SCIE) |

**In one line:** *Paper A* reports that perceived stress is associated more
strongly with the tinnitus **symptom** than with better-ear hearing loss, without
claiming causation or absence of a threshold association; *Paper B* builds and
stress-tests a **safety layer** for the rare, dangerous acute case hidden among
common benign "stress-related" tinnitus presentations.

## How the two papers relate

- **Paper A supplies the clinical motivation.** Because "stress-related tinnitus"
  is common and usually benign, the dangerous case is the **rare acute
  presentation hiding among many benign ones**. A cross-sectional association
  cannot justify dismissing measured, acute, or asymmetric hearing loss as
  "just stress."
- **Paper B supplies the safeguard.** It is the executed, results-bearing version
  of STARS's prospective safety component: a deterministic red-flag floor + honest
  measurement showing extraction (not the rules) is the bottleneck, so
  human-in-the-loop verification is required.

They are **complementary, not overlapping**: Paper A is *why it matters*, Paper B
is *how to make it safe*.

---

## Repository layout

| Folder | What it contains |
|--------|------------------|
| `paper/`   | **Paper A (STARS)** — LaTeX manuscript (sections, bibliography, tables, TikZ figures), standalone title page, cover letter, and the compiled PDF: the empirical stress–tinnitus–threshold survey study. |
| `paper02/` | **Paper B (SAFE-EAR)** — LaTeX manuscript, auto-generated result tables, result JSONs, and compiled PDF: the deterministic referral-safety layer, open benchmark, and the executed MedGemma evaluation. |
| `code/`    | Reproducible pipeline shared by both papers: survey-weighted KNHANES/NHANES analysis (Paper A) and the red-flag safety layer, open benchmark, extractors, MedGemma runner, and evaluation harness (Paper B), with tests. See `code/notebooks/` for the free-GPU MedGemma reproduction notebook. |
| `ppt/`     | English and Korean presentation decks (`pptxgenjs` source scripts + built `.pptx`). |
