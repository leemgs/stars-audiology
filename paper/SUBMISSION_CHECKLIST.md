# AJA Submission Readiness Checklist — STARS (v0.9)

Cross-checked against the *American Journal of Audiology* (AJA) / ASHA journals
author requirements. AJA is an ASHA journal: submissions go through the ASHA
online submission system, use **APA 7th-edition** style, and undergo
**masked (double-anonymized) peer review**.

> **Verify before submitting.** ASHA updates its author instructions
> periodically. Treat every "⚠️ verify" item below as *check the current AJA
> "Instructions for Authors" page and submission portal*, not as a settled fact.
> Items are marked ✅ present / ⚠️ needs attention / ❌ missing.

---

## 0. Article type — decide first (⚠️ highest-priority item)

The manuscript is framed as a **"Study Protocol / Pre-Analysis Plan with a
preliminary NHANES demonstration."** AJA does **not** advertise a standing
Registered Report / Protocol track the way some journals do. Before formatting
anything else, confirm with the editorial office **which AJA article category
this fits** (e.g., Research Article, Review Article, Clinical Focus, Tutorial).
The cover letter already asks the editor for guidance on category — good — but
be prepared to reframe as a **Research Article** (preliminary empirical results +
prespecified plan) if a protocol category is unavailable. This single decision
drives the word limits, abstract format, and structure below.

---

## 1. Manuscript structure & formatting

| Item | Status | Notes |
|------|--------|-------|
| Title page with full title, running head, all authors + affiliations | ✅ | In `main.tex`; running head "STARS / Stress, Tinnitus, and Hearing Outcomes". |
| **Masked ("blinded") manuscript** for review | ❌ | Current `main.tex` embeds author names, affiliations, emails, ORCID slots, and the identifiable GitHub URL (`github.com/leemgs/...`) throughout. ASHA uses anonymized review — prepare a **separate title page** and a **de-identified main document** (strip authors, affiliations, emails, the repo URL, and self-citations that reveal identity: `ha2022localization`, `kim2022bppv`, `kim2021ct`). |
| Double-spaced, 12 pt | ✅ | `\doublespacing`, `12pt` class option. |
| Continuous line numbers | ✅ | `lineno` package active. |
| Page numbers | ✅ | `fancyhdr` centered footer. |
| Title-page article-type / word-count block | ✅ | Present, but see word counts below. |

## 2. Abstract & keywords

| Item | Status | Notes |
|------|--------|-------|
| Structured abstract | ✅ | Purpose / Method / Results / Conclusions headings present. |
| Abstract word limit | ⚠️ verify | Abstract is **~320 words**; ASHA journals commonly cap abstracts near **200–250 words**. Confirm the AJA limit and trim if needed. |
| Keywords | ✅ | Present; consider trimming to the journal's max (often ≤ 5–6). |

## 3. References (APA 7th edition)

| Item | Status | Notes |
|------|--------|-------|
| **APA 7 reference style** | ⚠️ | **Converted** to APA 7 (alphabetical, `&`, italic journal+volume, DOIs as https links) and **filled full author lists for 5 of 6 "et al." entries** from the sources. Remaining: confirm the `hoffman2020noise` placeholder source and complete `mahboubi2013noise`'s issue/DOI — see `REVIEW_NOTES.md §1.4`. |
| In-text citations resolve | ✅ | All 17 `\citep` keys have matching entries; no orphan citations, no uncited entries (audited in `REVIEW_NOTES.md`). |
| Every reference cited & every citation referenced | ✅ | 17 cited ↔ 17 listed, verified. |
| Complete bibliographic data (vol/issue/pages/DOI) | ⚠️ | `chakrabarty2024depression` **completed** (vol/issue/pages/DOI). Remaining: `hoffman2020noise` (unverifiable placeholder — confirm source) and `mahboubi2013noise` (issue/DOI). See `REVIEW_NOTES.md §1`. |

## 4. Tables & figures

| Item | Status | Notes |
|------|--------|-------|
| All tables cited in text, in order | ✅ | 6 tables; `tab:ai` cross-reference **added** in this revision (was previously uncited). |
| All figures cited in text | ✅ | `fig:dag` cited; `fig:framework` cross-reference **added** in this revision (was previously uncited). |
| Table titles / figure captions self-contained | ✅ | Captions define abbreviations and the "synthetic ≠ result" caveat. |
| Figures legible / vector | ✅ | Both figures are TikZ (vector, scale cleanly). ⚠️ verify AJA's figure file-format/resolution rules if they require separate uploaded figure files rather than inline. |

## 5. Required disclosures & statements

| Item | Status | Notes |
|------|--------|-------|
| **Disclosure of Financial & Nonfinancial Relationships** | ✅ | Conflicts + funding declared. ⚠️ ASHA has a *specific* disclosure format/field in the portal — enter it there too, not only in the PDF. |
| Author contributions (CRediT) | ✅ | Present in Declarations. |
| Ethics / IRB statement | ✅ | Public deidentified data (Stages 1–2); Stage-3 IRB at Ajou. |
| Data availability | ✅ | KNHANES (KDCA access), NHANES (CDC), code repo. |
| Code availability | ✅ | GitHub repo stated. |
| **AI-use disclosure** | ✅ | Generative-AI drafting disclosed; model roles constrained. ASHA requires AI-use disclosure — good that it is explicit. |
| Reporting-guideline checklists (STROBE / TRIPOD+AI / SPIRIT) | ⚠️ | Manuscript *says* a completed checklist "accompanies the repository" — **ensure the filled STROBE and TRIPOD+AI checklists are actually committed and uploaded** as supplemental files. |
| ORCID for each author | ⚠️ | Placeholders `[to be added]` in the cover letter; add real ORCIDs in the portal. |

## 6. Cover letter

| Item | Status | Notes |
|------|--------|-------|
| Cover letter present | ✅ | `cover_letter.md` — strong; asks editor for article-category guidance. |
| Bracketed placeholders filled | ⚠️ | `[Date]`, editor name, ORCIDs still bracketed. |
| Originality / not-under-review statement | ✅ | Included. |
| Suggested reviewers | ⚠️ | Placeholder line present; add per AJA policy if requested. |

## 7. Consistency (see `REVIEW_NOTES.md` for detail)

| Item | Status | Notes |
|------|--------|-------|
| NHANES results in abstract = results = table = JSON | ✅ | All prevalence/OR/CI values match `code/outputs/nhanes_results.json` exactly. |
| **NHANES cycle window stated consistently** | ✅ | **Reconciled to 2017–2018** in `methods.tex` and `study_config.yaml` to match the committed results. See `REVIEW_NOTES.md §3.1`. |
| **KNHANES cycle window stated consistently** | ✅ | **Narrowed to 2010–2012 (KNHANES V)** across protocol text, config, and tables to match the mapping/CLI. See `REVIEW_NOTES.md §3.2`. |

---

## Pre-submission action list (ordered)

1. **Confirm the AJA article category** with the editorial office (drives everything else).
2. Produce the **masked manuscript + separate title page**; strip identifying content and identity-revealing self-citations from the review copy.
3. ~~Convert references to APA 7~~ (**done**) — ~~expand "et al." entries~~ (**5 of 6 done**); confirm the `hoffman2020noise` placeholder source and complete `mahboubi2013noise`'s issue/DOI.
4. Cycle windows ~~reconciliation~~ (**done**: NHANES 2017–2018; KNHANES narrowed to 2010–2012 / KNHANES V).
5. Trim the **abstract** to the AJA limit; trim keywords if needed.
6. Commit/upload the **filled STROBE + TRIPOD+AI checklists** as supplements.
7. Fill cover-letter placeholders (**date, editor, ORCIDs**) and add ORCIDs in the portal.
8. Enter **financial/nonfinancial disclosures** in the ASHA portal fields.
9. Re-build the PDF (`./build.sh`) and confirm no `??`/`[?]` cross-references remain.
