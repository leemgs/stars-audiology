# paper02 — SAFE-EAR (companion paper B)

**A Deterministic, Guideline-Derived Referral-Safety Layer over Open Medical-LLM
Extraction for Time-Critical Otologic Symptoms — An Open Benchmark and
Reproducible Evaluation.**

This is the **companion paper** to the STARS survey study in [`../paper/`](../paper).
STARS reports the empirical finding (perceived stress tracks the tinnitus symptom
more than the audiometric threshold) and specifies a prospective AI/safety
component; **this paper develops that safety/extraction component with real
results** on an open benchmark, and targets the *Journal of the American Medical
Informatics Association* (JAMIA) — a SCIE-indexed venue that is free to publish in
via its standard (non-open-access) route — rather than an audiology journal.
The manuscript follows JAMIA's *Research and Applications* format (structured
abstract, ICMJE/Vancouver numbered references).

## What is real here (and what is prospective)

- **Real results — deterministic layer:** a guideline-derived red-flag safety
  layer on a 71-case open benchmark (rule coverage **100%** recall / 0%
  over-referral). End-to-end safety is dominated by *extraction*, and the
  benchmark *discriminates* it.
- **Real results — an actual open medical LLM (MedGemma):** `google/medgemma-4b-it`
  was scored through the *same* harness and adapter as the rule-based references
  (deterministic decoding, run on a free-tier GPU). End-to-end red-flag recall
  spans **naive 56% → MedGemma-4b-it 78%** (14/18; specificity **100%**) **→ tuned
  100%** on identical cases; MedGemma macro-F1 **0.75**, urgency-changing error
  **10.8%**, run-consistency **1.00**. Because MedGemma never authored the
  benchmark nor saw its cue lists, **its 78% is an extractor-independent
  measurement** — the benchmark is neither saturated (a capable open medical LLM
  still misses 4/18) nor gamed (the tuned 100% reflects benchmark-specific
  tuning) — which resolves the circularity concern of a self-authored benchmark.
  The honest off-the-shelf expectation (~78%) is why clinician verification is
  load-bearing.
- **Still prospective:** evaluation on **real** clinical free text (rather than the
  open benchmark) needs IRB-approved, deidentified data; larger MedGemma variants
  and few-shot prompting remain to be tested.
- **No patient data:** every benchmark case is expert-authored or synthetic.

## Reproduce the results

From `../code/` — the rule-based references and unit tests run anywhere (no GPU):

```bash
python src/run_redflag_eval.py \
    --out ../paper02/outputs/redflag_eval.json \
    --latex-dir ../paper02/tables
python src/run_extraction_eval.py \
    --out ../paper02/outputs/extraction_eval.json \
    --latex ../paper02/tables/table_extraction.tex
python src/test_safety.py            # deterministic-layer unit tests
python src/test_llm_medgemma.py      # full LLM path, validated without weights
```

Reproduce the **MedGemma** row (needs a GPU + accepted MedGemma license + `HF_TOKEN`):

```bash
python src/run_llm_eval.py --extractor rule_v1,rule_v2,medgemma \
    --model google/medgemma-4b-it \
    --out ../paper02/outputs/llm_extractor_eval.json \
    --latex ../paper02/tables/table_llm_compare.tex
```

No local GPU? Open the turnkey **free-GPU notebook**
[`code/notebooks/medgemma_eval_colab.ipynb`](../code/notebooks/medgemma_eval_colab.ipynb)
(Colab/Kaggle free-tier T4 is enough for the 4B model).

Benchmark and code: `code/src/redflag_benchmark.py`, `safety.py`,
`llm_extract.py`, `llm_medgemma.py`, `run_redflag_eval.py`,
`run_extraction_eval.py`, `run_llm_eval.py`.

## Build the PDF

```bash
cd paper02 && bash build.sh      # tectonic or pdflatex; writes main.pdf
```

| File | What |
|------|------|
| `main.tex` | Self-contained manuscript (inline bibliography) |
| `tables/`  | Auto-generated result tables (`\input` by `main.tex`) |
| `outputs/` | Result JSONs produced by the evaluation scripts |
