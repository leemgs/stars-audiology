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
stress tracks the tinnitus _symptom_ but not the audiometric _threshold_** once
occupational noise and age are accounted for — a **symptom-vs-threshold
dissociation**. Intuitively: stress is entangled with *how much a person is
bothered by / reports* tinnitus, not with the *actual cochlear damage* measured
by pure-tone audiometry.

### Core contributions
1. **A prespecified, survey-weighted, reproducible result** — stress ↔ tinnitus
   **OR 1.42** (95% CI 1.26–1.60, *p*<0.001) vs. stress ↔ hearing threshold
   **OR 1.18** (0.99–1.41, *n.s.* after adjusting for noise and age); NHANES gives
   directionally consistent support under a distress proxy.
2. **An open, reproducible analysis scaffold** — harmonized variable mappings,
   design-based estimators (domain estimation, conservative single-PSU handling),
   model cards, and a synthetic-data path, so every number can be regenerated.
3. **A prespecified plan (design only, no results)** for prospective components:
   cross-national external validation and a clinician-governed, safety-gated
   AI-extraction/referral component (the latter is executed *with results* in
   Paper B).

> **What Paper A does _not_ claim.** It is **cross-sectional**, so it reports an
> **association, not causation**, and does **not** show that stress *causes* or
> that stress management *prevents* tinnitus (reverse causation — bothersome
> tinnitus raising stress — cannot be excluded). Clinically it supports
> *considering* stress when counseling patients with **stable** tinnitus, while
> **cautioning against attributing acute or asymmetric hearing loss to "stress"** —
> which is exactly the danger Paper B guards against.

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
| **Headline result** | Stress → **tinnitus OR 1.42** (p<0.001) but **threshold OR 1.18** (n.s.): a **symptom-vs-threshold dissociation** | Rule coverage **100%**; end-to-end recall **naive 56% → MedGemma 78% → tuned 100%** → **extraction is the safety bottleneck** |
| **Role of AI** | None in the result; AI/safety is a *prospective plan* | AI/LLM extraction **is the subject**; a real MedGemma eval is executed and **resolves circularity** |
| **Claim discipline** | Association, **not** causation or prevention | A finite-set 100% is a *target*, not a deployment guarantee |
| **Target venue** | *American Journal of Audiology* (SCIE) | *Journal of the American Medical Informatics Association*, JAMIA (SCIE) |

**In one line:** *Paper A* establishes, on real survey data, that stress is tied to
the tinnitus **symptom** more than to measured hearing **damage**; *Paper B* builds
and stress-tests the **safety layer** that stops an AI pipeline from missing the
rare, dangerous acute case hidden among common benign "stress-related" tinnitus.

## How the two papers relate

- **Paper A supplies the clinical motivation.** Because "stress-related tinnitus"
  is common and usually benign, the dangerous case is the **rare acute
  presentation hiding among many benign ones** — and stress does *not* track the
  real audiometric damage, so "it's just stress" is an unsafe default.
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
