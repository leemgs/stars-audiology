#!/usr/bin/env bash
# Build the SAFE-EAR companion paper (paper B).
# Requires a LaTeX engine. With a full TeX Live:
#   pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
# Or with tectonic (self-contained, fetches packages on first run):
#   tectonic -o . main.tex
set -euo pipefail
if command -v tectonic >/dev/null 2>&1; then
  tectonic -o . main.tex
else
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex   # second pass resolves refs
fi
echo "Built paper02/main.pdf"
