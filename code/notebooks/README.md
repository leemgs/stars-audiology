# Running the MedGemma evaluation on a free GPU

The SAFE-EAR harness (`code/src/run_llm_eval.py`) scores an **actual open medical
LLM (MedGemma)** on the same prespecified benchmark, schema-to-feature adapter,
and metrics as the rule-based references. The model is a gated, GPU-dependent
download, so it cannot run in the restricted CI sandbox — but it runs fine on a
**free** GPU.

## Fastest path: `medgemma_eval_colab.ipynb`

1. Open the notebook in **Google Colab** (`File → Upload notebook`, or push to a
   Gist and use *Open in Colab*) or **Kaggle Notebooks**.
2. Select a **GPU** runtime. A free **T4 (16 GB)** is enough for
   `google/medgemma-4b-it` (~8 GB in bf16).
3. Accept the MedGemma license once at
   <https://huggingface.co/google/medgemma-4b-it> (free) and create a read token
   at <https://huggingface.co/settings/tokens>.
4. `Run all`. The final cell prints `llm_extractor_eval.json`.
5. Paste that JSON back into the Claude chat — Claude inserts the measured
   MedGemma row into the paper and finalizes it.

The notebook installs deps, logs in to Hugging Face, clones this repo, runs

```
python run_llm_eval.py --extractor rule_v1,rule_v2,medgemma \
    --model google/medgemma-4b-it --out /content/llm_extractor_eval.json
```

and shows the result. Decoding is greedy (deterministic); the 37-note benchmark
takes a few minutes on a T4.

## Other free options

- **Kaggle Notebooks** — 30 GPU-hours/week free (T4×2 or P100). Same steps; the
  notebook already falls back to the working directory for the output path.
- **Hugging Face Spaces** (free CPU, or a short community-GPU grant) — clone the
  repo and run the same command; CPU works for the 4B model but is slow.
- **Lightning AI Studio / Paperspace free tiers** — any environment with a
  ~16 GB GPU and internet to Hugging Face works.

## What comes back

`llm_extractor_eval.json` contains, for each extractor, the field-level metrics
(macro P/R/F1, document-exact match, urgency-changing error rate, run
consistency) and the end-to-end red-flag recall/specificity with Wilson CIs and a
per-category breakdown — the numbers the manuscript needs for the MedGemma row.
Because MedGemma is developed independently of this benchmark's cue lists, its
end-to-end recall is an extractor-independent check on the rule-based results.
