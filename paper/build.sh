#!/usr/bin/env bash
set -euo pipefail
pdflatex -interaction=nonstopmode main.tex
bibtex main || true
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cp main.pdf HEAR-WORK_AI_AJA_public_dataset_manuscript_v0.7.pdf
