# Building the STARS manuscript (`main.tex`)

This folder holds the LaTeX source for the STARS manuscript targeted at the
*American Journal of Audiology* (AJA). `main.tex` is the root document; it
`\input`s every section (`sections/`) and table (`tables/`), and draws the two
figures inline with **TikZ** (no external image files).

## TL;DR

```bash
cd paper
./build.sh          # runs pdflatex -> bibtex -> pdflatex x2, then copies the PDF
```

Output: `main.pdf` (also copied to `STARS_AJA_public_dataset_manuscript_v0.9.pdf`).

## What you need

A full TeX distribution — **TeX Live 2021 or newer** (or MacTeX, which bundles
TeX Live). MiKTeX works too and will fetch packages on demand. The document
uses only mainstream packages, all shipped with a *full* TeX Live install:

`geometry`, `lmodern`, `setspace`, `booktabs`, `longtable`, `array`,
`graphicx`, `hyperref`, `amsmath`, `authblk`, `natbib`, `lineno`, `enumitem`,
`xcolor`, `microtype`, `url`, `fontenc`, `inputenc`, `tikz` (with the
`shapes.geometric`, `arrows.meta`, `positioning`, `fit`, `backgrounds`
libraries), and `fancyhdr`.

Install a full TeX Live so no package is missing mid-build:

| Platform | Command |
|----------|---------|
| Debian/Ubuntu | `sudo apt-get install texlive-full` |
| Fedora | `sudo dnf install texlive-scheme-full` |
| macOS | `brew install --cask mactex` (or the smaller `basictex` + `tlmgr install ...`) |
| Windows | Install TeX Live or MiKTeX from their official installers |

Check the toolchain is on your `PATH`:

```bash
pdflatex --version
bibtex   --version
```

## How to build

### Option A — the provided script (recommended)

```bash
cd paper
./build.sh
```

`build.sh` runs the standard four-pass LaTeX sequence:

```
pdflatex main.tex   # 1st pass: writes .aux (labels, citations)
bibtex   main       # resolves \cite keys
pdflatex main.tex   # 2nd pass: pulls in the bibliography
pdflatex main.tex   # 3rd pass: settles all cross-references / page numbers
```

The multiple passes are required so that `\ref`, `\citep`, line numbers, and the
running head resolve correctly. It finishes by copying `main.pdf` to the
versioned filename.

### Option B — `latexmk` (handles the passes for you)

```bash
cd paper
latexmk -pdf main.tex      # runs as many passes as needed
latexmk -c                 # optional: clean aux files (keeps the PDF)
```

### Option C — Overleaf / no local install

Upload the **entire `paper/` folder** (preserving the `sections/` and `tables/`
subfolders) to a new Overleaf project, set **`main.tex`** as the main document,
and set the compiler to **pdfLaTeX**. It builds as-is.

### Option D — Docker (reproducible, no host install)

```bash
cd paper
docker run --rm -v "$PWD":/work -w /work texlive/texlive:latest ./build.sh
```

### Masked-review build (ASHA double-anonymized submission)

AJA uses masked peer review, so you submit **two** things: a non-anonymized
**title page** and an **anonymized manuscript**.

- **Title page** — compile the standalone `title_page.tex` (authors,
  affiliations, corresponding author, CRediT, ORCID slots, funding, conflicts,
  AI-use disclosure):
  ```bash
  pdflatex title_page.tex
  ```
- **Anonymized manuscript** — build `main.tex` with the blinding toggle on. It
  suppresses the author block, the corresponding-author/CRediT identities, and
  the repository URLs:
  ```bash
  pdflatex -interaction=nonstopmode "\def\BLIND{}\input{main.tex}"
  bibtex   main
  pdflatex -interaction=nonstopmode "\def\BLIND{}\input{main.tex}"
  pdflatex -interaction=nonstopmode "\def\BLIND{}\input{main.tex}"
  ```
  The normal `./build.sh` (no `\def\BLIND{}`) still produces the full,
  non-anonymized PDF — the toggle defaults to off.

  **Not auto-masked** (would damage the text if stripped programmatically), so
  handle manually before submitting the anonymized copy: identity-revealing
  self-citations (`ha2022localization`, `kim2022bppv`, `kim2021ct`) and in-text
  institution mentions (e.g., "Ajou University Hospital" in Methods, Figure~1,
  and Declarations). Soften these to neutral phrasing in a review copy.

### Reporting checklists

Filled STROBE and TRIPOD+AI checklists live in `checklists/` and map each item
to the manuscript section that addresses it. Upload them as supplemental files
(the Declarations section refers to them).

## A note on the bibliography

The manuscript currently renders its reference list from a **manual**
`thebibliography` environment in `sections/references_manual.tex`, with
`natbib` providing the `\citep{...}` author–year citations. Because the entries
are hard-coded there, the `bibtex main` step in `build.sh` is effectively a
no-op — it neither helps nor breaks the build (`build.sh` guards it with
`|| true`), so you may see a harmless "I found no \bibdata command" message.

`references.bib` holds the same 17 entries in BibTeX form and is kept as the
machine-readable source of truth, but it is **not** wired into `main.tex`. If
you prefer BibTeX-driven references (recommended before final submission, since
AJA uses APA 7th-edition style), switch `main.tex` to use it:

```latex
% replace  \input{sections/references_manual}  with:
\bibliographystyle{apalike}   % or an APA-7 style such as apa7/apacite
\bibliography{references}
```

then keep the `bibtex` pass in the build. Until that switch is made, edit
`sections/references_manual.tex` for any reference change and mirror it in
`references.bib` so the two do not drift.

## Files at a glance

```
paper/
├── main.tex                 # root document (edit \input order here; \ifblind toggle)
├── title_page.tex           # standalone non-anonymized title page (masked submission)
├── build.sh                 # 4-pass build + copy to versioned PDF
├── references.bib           # BibTeX source (not currently wired in; see above)
├── sections/                # abstract, introduction, methods, results, ...
│   └── references_manual.tex# the reference list actually rendered
├── tables/                  # table_*.tex (all \input from main.tex)
├── checklists/              # filled STROBE + TRIPOD+AI reporting checklists
├── SUBMISSION_CHECKLIST.md  # AJA submission readiness checklist
└── REVIEW_NOTES.md          # bibliography + manuscript/code consistency audit
```

## Troubleshooting

- **`! LaTeX Error: File 'tikz.sty' not found` (or similar):** your TeX install
  is not the *full* scheme. Install `texlive-full` / `texlive-scheme-full`, or
  `tlmgr install pgf lineno authblk enumitem microtype` for the specific
  missing packages.
- **Cross-references show as `??` or citations as `[?]`:** you did not run
  enough passes. Use `./build.sh` or `latexmk -pdf`, which run all passes.
- **Line numbers / running head look wrong on page 1:** these settle on the
  final pass; rebuild fully rather than running a single `pdflatex`.
