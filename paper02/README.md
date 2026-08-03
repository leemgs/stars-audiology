# paper02 — SAFE-EAR (companion paper B)

**A Deterministic, Guideline-Derived Referral-Safety Layer over Open Medical-LLM
Extraction for Time-Critical Otologic Symptoms — An Open Benchmark and
Reproducible Evaluation.**

This is the **companion paper** to the STARS survey study in [`../paper/`](../paper).
STARS reports the empirical finding (perceived stress tracks the tinnitus symptom
more than the audiometric threshold) and specifies a prospective AI/safety
component; **this paper develops that safety/extraction component with real
results** on an open benchmark, and targets a digital-health / medical-informatics
venue rather than an audiology journal.

## What is real here (and what is prospective)

- **Real results:** a deterministic red-flag safety layer evaluated on an open
  benchmark (rule coverage **100%** recall / 0% over-referral; **end-to-end 82%**
  recall bounded by extraction), and a reproducible rule-based extraction baseline
  (macro-F1 **0.87**, urgency-changing error **14%**, run-consistency **1.00**).
- **Prospective:** evaluation of an actual open medical LLM (e.g., MedGemma) on
  clinical free text needs model access and IRB-approved data. The benchmark and
  metrics are fixed here so that comparison is prespecified.
- **No patient data:** every case is expert-authored or synthetic.

## Reproduce the results

From `../code/`:

```bash
python src/run_redflag_eval.py \
    --out ../paper02/outputs/redflag_eval.json \
    --latex-dir ../paper02/tables
python src/run_extraction_eval.py \
    --out ../paper02/outputs/extraction_eval.json \
    --latex ../paper02/tables/table_extraction.tex
python src/test_safety.py        # deterministic-layer unit tests
```

Benchmark and code: `code/src/redflag_benchmark.py`, `safety.py`,
`run_redflag_eval.py`, `run_extraction_eval.py`.

## Build the PDF

```bash
cd paper02 && bash build.sh      # tectonic or pdflatex; writes main.pdf
```

| File | What |
|------|------|
| `main.tex` | Self-contained manuscript (inline bibliography) |
| `tables/`  | Auto-generated result tables (`\input` by `main.tex`) |
| `outputs/` | Result JSONs produced by the evaluation scripts |
