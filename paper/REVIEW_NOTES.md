# STARS v0.9 — Bibliography & Manuscript/Code Consistency Audit

Two audits in one document:
1. Bibliography organization & verification (`§1`).
2. Manuscript ↔ code/data consistency (`§2`–`§3`).

Status legend: ✅ verified OK · ⚠️ needs attention · ❌ defect · 🔧 fixed in this revision.

---

## §1. Bibliography

### 1.1 Structure — how references are wired

- `main.tex` renders references from a **manual** `thebibliography` in
  `sections/references_manual.tex`; `natbib` supplies `\citep`. The BibTeX file
  `references.bib` holds the same entries but is **not** `\input`/`\bibliography`d
  into the build (so `bibtex main` in `build.sh` is a harmless no-op).
- **Risk:** the manual list and `references.bib` can silently drift. **Right now
  they are in sync** (see 1.2). Before final submission, prefer switching to
  BibTeX + an APA-7 style (see `README.md` → "A note on the bibliography").

### 1.2 Completeness — citations ↔ entries

- **17** distinct `\citep` keys used across the manuscript.
- **17** `\bibitem` entries in `references_manual.tex`.
- **17** entries in `references.bib`.
- ✅ **Every cited key has an entry; every listed entry is cited.** No orphan
  citations, no uncited "ghost" references. Key sets match exactly across all
  three (cited / manual list / `.bib`):

  `baigi2011tinnitus, chakrabarty2024depression, chandrasekhar2019ssnhl,
  collins2024tripodai, ha2022localization, hoffman2020noise, joo2015hrqol,
  kim2021ct, kim2022bppv, mahboubi2013noise, mccormack2016review,
  medgemma2025blog, medgemma2026docs, park2014tinnitus, tunkel2014cpg,
  vonelm2007strobe, who2021world`

### 1.3 Accuracy — spot-checked entries

Bibliographic details verified as correct for the well-known sources:

| Key | Check | Status |
|-----|-------|--------|
| `vonelm2007strobe` | *Ann Intern Med* 2007;147(8):573–577; doi:10.7326/0003-4819-147-8-200710160-00010 | ✅ |
| `collins2024tripodai` | *BMJ* 2024;385:e078378; doi:10.1136/bmj-2023-078378 | ✅ |
| `tunkel2014cpg` | *Otolaryngol Head Neck Surg* 2014;151(2_suppl):S1–S40; doi:10.1177/0194599814545325 | ✅ |
| `chandrasekhar2019ssnhl` | *OHNS* 2019;161(1_suppl):S1–S45; doi:10.1177/0194599819859885 | ✅ |
| `baigi2011tinnitus` | *Ear Hear* 2011;32(6):787–789; doi:10.1097/AUD.0b013e31822229bd | ✅ |
| `mccormack2016review` | *Hear Res* 2016;337:70–79; doi:10.1016/j.heares.2016.05.009 | ✅ |
| `park2014tinnitus` | *J Epidemiol* 2014;24(5):417–426 (KNHANES 2009–2011 tinnitus) | ✅ |
| `joo2015hrqol` | *PLoS ONE* 2015;10(6):e0131247 | ✅ |
| `who2021world` | WHO, *World Report on Hearing*, 2021 | ✅ |

### 1.4 Issues to fix

- ⚠️ **Incomplete entries** (add missing fields before submission):
  - `chakrabarty2024depression` — no volume/issue/pages/DOI; author list is "et al." only.
  - `hoffman2020noise` — vague "CDC/NIOSH report"; needs a proper report number/URL or reclassification.
  - `mahboubi2013noise` — has volume 270 but no issue/pages-within-issue/DOI.
- ⚠️ **Minor drift** between the two sources: in `references.bib` the
  `mahboubi2013noise` title ends "…hearing loss: National Health and Nutrition
  Examination Surveys", but the manual `\bibitem` truncates it at "…hearing
  loss." Harmonize.
- ❌ **Style is not APA 7** (AJA requirement). The list uses a Vancouver/author-year
  hybrid (`doi:` prefixes, abbreviated journal handling, in-list "et al."). Convert
  to APA 7 (`Author, A. A., & Author, B. B. (Year). Title. *Journal, Vol*(Issue),
  pp. https://doi.org/...`). See `SUBMISSION_CHECKLIST.md §3`.

---

## §2. Manuscript ↔ code/data consistency — numbers

**Result:** ✅ The reported NHANES numbers match the committed results file
`code/outputs/nhanes_results.json` **exactly**. No fabricated or drifted values.

| Quantity | Manuscript (abstract / results / `table_results.tex`) | `nhanes_results.json` | Status |
|----------|-------------------------------------------------------|-----------------------|--------|
| Tinnitus prevalence | 28.5% (26.5–30.4), n=5,354 | 0.2846 (0.2652–0.3040), n=5354 | ✅ |
| Hearing-loss prevalence | 12.0% (10.4–13.6), n=4,808 | 0.1199 (0.1038–0.1359), n=4808 | ✅ |
| Depression (PHQ-9≥10) prevalence | 8.4% (7.5–9.4), n=7,293 | 0.0843 (0.0750–0.0936), n=7293 | ✅ |
| Tinnitus ~ occ. noise | OR 1.59 (1.32–1.92)*** | 1.593 (1.321–1.921) | ✅ |
| Tinnitus ~ depressed | OR 1.61 (1.23–2.11)*** | 1.611 (1.232–2.107) | ✅ |
| Tinnitus ~ age | OR 1.00 (0.98–1.01) | 0.997 (0.984–1.010) | ✅ |
| Tinnitus ~ female sex | OR 1.61 (1.35–1.91)*** | 1.607 (1.348–1.915) | ✅ |
| Hearing loss ~ occ. noise | OR 1.22 (0.94–1.58) | 1.217 (0.936–1.584) | ✅ |
| Hearing loss ~ depressed | OR 2.29 (1.56–3.35)*** | 2.289 (1.565–3.349) | ✅ |
| Hearing loss ~ age | OR 1.11 (1.09–1.13)*** | 1.111 (1.092–1.131) | ✅ |
| Hearing loss ~ female sex | OR 0.42 (0.29–0.61)*** | 0.422 (0.292–0.611) | ✅ |
| Analytic N (tinnitus / HL assoc.) | 4,603 / 4,463 | 4603 / 4463 | ✅ |

Synthetic-scaffold metrics in `table_metrics.tex` (Tinnitus AUROC 0.64 / AUPRC
0.49 / Brier 0.20) also match `code/outputs/metrics_tinnitus_status.json`
(0.6423 / 0.4927 / 0.2030). ✅ And they are correctly and repeatedly labeled
"not a result."

---

## §3. Manuscript ↔ code/data consistency — study windows (⚠️ reconcile)

Two survey-window descriptions are internally inconsistent. Neither is a number
error, but both will draw a reviewer's eye and should be reconciled to a single
statement across prose, config, and outputs.

### 3.1 ⚠️ NHANES cycle window — three different statements

| Location | Says |
|----------|------|
| `sections/methods.tex` | "2011–2012, 2015–2016, and **2017–March 2020**" |
| `code/config/study_config.yaml` (`validation_cycles`) | `2011-2012, 2015-2016, **2017-2020**` |
| `sections/results.tex`, `sections/abstract.tex`, `tables/table_results.tex`, `code/outputs/nhanes_results.json` | "2011–2012, 2015–2016, **2017–2018**" |
| `cover_letter.md` | "pooled **2011–2018**" |

The **actual analysis that produced the committed results used 2017–2018**
(three two-year cycles). The protocol text/config describe **2017–2020** (the
pre-pandemic combined file). **Pick one:**
- (a) If the demo really used 2017–2018, change `study_config.yaml` and
  `methods.tex` to say 2017–2018 (and fix the cover letter's loose "2011–2018").
- (b) If 2017–2020 is intended, re-run `nhanes_analysis.py` over the 2017–2020
  pre-pandemic file and refresh the results/table.

*Not auto-fixed here — this is an analytic-scope decision for the authors.*

### 3.2 ⚠️ KNHANES cycle window — 2009 present in protocol, absent in implementation

| Location | Says |
|----------|------|
| `sections/methods.tex`, `code/config/study_config.yaml` | KNHANES **2009–2012** |
| `code/config/knhanes_mapping.yaml` (`files`), `knhanes_analysis.py` default `--cycles` | **2010–2012** only (no 2009) |

Either add a `2009` file entry (`HN09_ALL.sas7bdat`) to the mapping and include
`2009` in `--cycles`, or narrow the protocol text to 2010–2012. See
`code/config/KNHANES_MAPPING_VERIFICATION.md`.
*Not auto-fixed — analytic-scope decision.*

---

## §4. Cross-references (LaTeX) — fixed here

- 🔧 `Table~\ref{tab:ai}` (AI components table) was **defined but never cited**
  in the body → added a cross-reference in `sections/ai_system.tex`
  ("Model Roles and Prohibitions").
- 🔧 `Figure~\ref{fig:framework}` (conceptual framework) was **defined but never
  cited** → added a cross-reference in `sections/methods.tex` ("Study Design").
- ✅ All other `\ref` targets (`fig:dag`, `tab:datasets`, `tab:variables`,
  `tab:harmonization`, `tab:intended`, `tab:metrics`, `tab:redflag`,
  `tab:results`, `sec:ai`) resolve; `tab:results_knhanes` is guarded by
  `\IfFileExists`, so it is fine to be absent until the KNHANES table exists.

---

## Summary of what was changed vs. left for author decision

**Fixed in this revision (safe, unambiguous):**
- Added the two missing in-text float cross-references (`tab:ai`, `fig:framework`).

**Left for the authors (scope / style decisions, documented above):**
- NHANES 2017–2018 vs 2017–2020 reconciliation (§3.1).
- KNHANES 2009 inclusion (§3.2).
- APA-7 reference-style conversion + three incomplete entries (§1.4).
- Wiring `references.bib` into the build vs. keeping the manual list (§1.1).
