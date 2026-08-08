# STARS v0.9 — Bibliography & Manuscript/Code Consistency Audit

Two audits in one document:
1. Bibliography organization & verification (`§1`).
2. Manuscript ↔ code/data consistency (`§2`–`§3`).

Status legend: ✅ verified OK · ⚠️ needs attention · ❌ defect · 🔧 fixed in this revision.

> **Historical note (post-audit reorganization).** This audit predates the
> two-paper split. The AI/prediction component and its LaTeX artifacts —
> `sections/ai_system.tex` and `tables/table_ai.tex`, `table_metrics.tex`,
> `table_redflag.tex`, `table_intended_use.tex`, plus the `TRIPOD-AI_checklist.md`
> — were subsequently moved out of Paper A into the companion SAFE-EAR paper
> (`../paper02/`). References below to those files are therefore historical:
> Paper A is now a purely observational (STROBE) study, and the AI content,
> benchmark, and TRIPOD+AI checklist live under `../paper02/`.

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
  collins2024tripodai, ha2022localization, hoffman2017declining, joo2015hrqol,
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

### 1.4 Issues — style converted, author lists still to complete

- 🔧 **APA 7 conversion done.** `sections/references_manual.tex` was rewritten in
  APA 7 style: alphabetical order, `&` before the final author, year in
  parentheses after the authors, italicized journal + volume, issue in
  parentheses, en-dash page ranges, and DOIs as `https://doi.org/...` links. The
  `mahboubi` title drift was harmonized to the full title, and the derivable
  PLOS ONE DOI was added for `joo2015hrqol` (mirrored in `references.bib`).
- 🔧 **Full author lists filled from the source publications** (verified via web
  search of the journals/PubMed, mirrored into `references.bib`):
  - `chakrabarty2024depression` — Chakrabarty, S., Mudar, R., Chen, Y., & Husain,
    F. T. (2024). *Ear and Hearing, 45*(3), 775–786.
    doi:10.1097/AUD.0000000000001467. Title corrected "population data" →
    "population study"; volume/issue/pages/DOI added.
  - `chandrasekhar2019ssnhl` — all 17 authors listed.
  - `collins2024tripodai` — 34 authors → APA 21+ rule (first 19, ellipsis, Logullo).
  - `park2014tinnitus` — all 12 authors; "Surveys" → "Survey" per the real title;
    doi:10.2188/jea.JE20140024 added.
  - `tunkel2014cpg` — 23 authors → APA 21+ rule (first 19, ellipsis, Whamond).
- 🔧 **`hoffman2020noise` placeholder → replaced with the verified real source.**
  No 2020 report titled "Noise exposure and hearing loss: Data from U.S. health
  surveys" exists; the entry was a placeholder. Cross-checked against JAMA
  Network + PubMed + Wikidata and replaced with the Hoffman-first-author NHANES
  paper it was standing in for: **Hoffman, H. J., Dobie, R. A., Losonczy, K. G.,
  Themann, C. L., & Flamme, G. A. (2017). Declining prevalence of hearing loss
  in US adults aged 20 to 69 years. *JAMA Otolaryngology–Head & Neck Surgery,
  143*(3), 274–285. https://doi.org/10.1001/jamaoto.2016.3527**. The BibTeX/
  bibitem **key was renamed `hoffman2020noise` → `hoffman2017declining`** and the
  single `\citep` in `related_work.tex` updated to match. Entry type changed
  `@techreport` → `@article`.
- 🔧 **`mahboubi2013noise` completed.** Added issue and DOI (cross-checked via
  Springer + Wikidata): *European Archives of Oto-Rhino-Laryngology, 270*(**2**),
  461–467, **https://doi.org/10.1007/s00405-012-1979-6**.

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

### 3.1 🔧 NHANES cycle window — reconciled to 2017–2018

**Resolved** by matching the prose/config to the window the committed results
were actually computed on (2017–2018, three two-year cycles):
- `sections/methods.tex`: "2017–March 2020" → **"2017–2018"**.
- `code/config/study_config.yaml` (`validation_cycles`): "2017-2020" → **"2017-2018"**.
- `cover_letter.md`'s "pooled 2011–2018" is consistent with this endpoint and
  was left as a shorthand range.

All NHANES-window statements now agree with `code/outputs/nhanes_results.json`
(`cycles: 2011-2012, 2015-2016, 2017-2018`). If you later decide to *extend* to
the 2017–2020 pre-pandemic file instead, re-run `nhanes_analysis.py` on it and
refresh the results/table + these strings.

### 3.2 🔧 KNHANES cycle window — narrowed to 2010–2012 (KNHANES V)

**Resolved** by narrowing the protocol to match the implementation
(`knhanes_mapping.yaml` `files` and the `knhanes_analysis.py` default `--cycles`
already covered 2010–2012 only). Updated:
- `code/config/study_config.yaml`: `development_cycles` → **`["2010","2011","2012"]`** ("KNHANES V").
- `sections/methods.tex`: "KNHANES IV–V, 2009–2012" → **"KNHANES V, 2010–2012"**.
- `sections/public_data.tex`: audiometry-cycle phrase → **"2010–2012"**.
- `tables/table_harmonization.tex`: KNHANES source column → **"Otologic Q, 2010–2012"** (both tinnitus rows).

Note: the `park2014tinnitus` reference title legitimately contains "…Surveys
2009–2011" (the real published title) and was **left unchanged**.

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
- Reconciled the NHANES cycle window to **2017–2018** across `methods.tex` and
  `study_config.yaml` (§3.1).
- Converted the reference list to **APA 7** style (§1.4); mirrored the PLOS ONE
  DOI into `references.bib`.
- Filled **full author lists** for five previously-"et al." entries from the
  source publications (§1.4), with corrected titles/DOIs, mirrored into
  `references.bib`.
- Replaced the unverifiable `hoffman2020noise` placeholder with the verified
  **Hoffman et al. (2017)** JAMA Otolaryngol paper (key renamed to
  `hoffman2017declining`, `\citep` updated) and **completed `mahboubi2013noise`**
  (issue + DOI) — both cross-checked online (§1.4).

- Narrowed the KNHANES window to **2010–2012 (KNHANES V)** across
  `study_config.yaml`, `methods.tex`, `public_data.tex`, and
  `table_harmonization.tex` (§3.2).

- Replaced the `hoffman2020noise` placeholder with the verified Hoffman et al.
  (2017) source (key → `hoffman2017declining`) and completed `mahboubi2013noise`
  (issue + DOI), both cross-checked online (§1.4).

**Left for the authors (build choice only):**
- Wiring `references.bib` into the build vs. keeping the manual list (§1.1).

All reference entries now carry complete, verified bibliographic data.
