"""Open medical-LLM (MedGemma) extractor for the STARS safety harness.

This wires an **actual** open medical LLM into the *same* evaluation harness used
for the rule-based references (``redflag_benchmark.EXTRACTORS``), so the open-LLM
red-flag recall/specificity are measured against the identical, prespecified gold
benchmark. The model is loaded through Hugging Face ``transformers`` and decoded
deterministically (greedy), constrained to emit the fixed extraction schema
(``llm_extract.EXTRACTION_SCHEMA``); its JSON is mapped to safety features by
``redflag_benchmark.schema_to_features``.

Why a separate module. The model is a gated download (``google/medgemma-4b-it``)
and typically needs a GPU, so it cannot be vendored into the repo or executed in
a restricted CI sandbox. Everything here is nonetheless *concrete and runnable*:

* ``load_medgemma()`` builds a real ``generate(prompt) -> str`` from transformers.
* ``build_medgemma_extractor()`` returns a ``note -> feature-dict`` callable that
  plugs straight into ``run_llm_eval.py`` and the red-flag/extraction evaluators.
* ``ScriptedGenerator`` is a deterministic stand-in that returns schema JSON for a
  note **without any model**, so the full text -> JSON -> features -> safety ->
  metrics path is unit-tested (``test_llm_medgemma.py``) and validated end to end
  even where the weights are unavailable. It is a harness self-test only and is
  never reported as a model result.

Reproduce the real evaluation where model access exists (accept the MedGemma
license, set ``HF_TOKEN``, GPU recommended)::

    pip install "transformers>=4.43" accelerate torch
    python src/run_llm_eval.py --extractor medgemma \
        --model google/medgemma-4b-it \
        --out ../paper02/outputs/llm_extractor_eval.json
"""
from __future__ import annotations

import json
import re
from typing import Callable, Dict, List, Optional

from llm_extract import EXTRACTION_SCHEMA, extract_with_prompt_template
from redflag_benchmark import schema_to_features

DEFAULT_MODEL = "google/medgemma-4b-it"

Generate = Callable[[str], str]


# --------------------------------------------------------------------------- #
# Robust JSON extraction: real LLMs wrap JSON in code fences or prose. We strip
# fences, locate the first balanced object, and fall back to all-"unknown" (the
# safe/conservative default) if nothing parses.
# --------------------------------------------------------------------------- #
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _first_json_object(text: str) -> Optional[str]:
    """Return the first brace-balanced ``{...}`` substring, or None."""
    start = text.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start:i + 1]
        start = text.find("{", start + 1)
    return None


def robust_parse_fields(raw: str) -> Dict[str, str]:
    """Parse an LLM's raw output into the extraction schema.

    Tolerates code fences and surrounding prose. Missing keys default to
    ``"unknown"`` so downstream mapping is conservative (a rule can only fire on
    an affirmative field). This never raises.
    """
    candidate = raw
    m = _FENCE.search(raw)
    if m:
        candidate = m.group(1)
    obj = _first_json_object(candidate) or _first_json_object(raw)
    fields: Dict[str, str] = {}
    if obj is not None:
        try:
            parsed = json.loads(obj)
            if isinstance(parsed, dict):
                fields = {str(k): v for k, v in parsed.items()}
        except json.JSONDecodeError:
            fields = {}
    for key in EXTRACTION_SCHEMA:
        fields.setdefault(key, "unknown")
    return fields


def build_extractor_from_generate(generate: Generate) -> Callable[[str], Dict[str, bool]]:
    """Wrap a ``generate(prompt) -> str`` into a ``note -> feature-dict`` extractor
    that emits the SAME boolean feature keys as the rule-based extractors."""
    def _extract(note: str) -> Dict[str, bool]:
        raw = generate(extract_with_prompt_template(note))
        return schema_to_features(robust_parse_fields(raw))
    return _extract


# --------------------------------------------------------------------------- #
# Real MedGemma loader (transformers). Deterministic greedy decoding.
# --------------------------------------------------------------------------- #
def load_medgemma(model_id: str = DEFAULT_MODEL,
                  max_new_tokens: int = 256,
                  device: Optional[str] = None,
                  dtype: str = "auto",
                  hf_token: Optional[str] = None) -> Generate:
    """Load a MedGemma (Gemma-family) instruct model and return a deterministic
    ``generate(prompt) -> str``. Requires ``transformers`` (and typically a GPU);
    raises a clear ImportError/OSError if unavailable so callers can skip."""
    import os

    import torch  # noqa: F401  (imported for side effect / availability check)
    from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer

    token = hf_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = ("auto" if dtype == "auto"
                   else getattr(torch, dtype))

    # MedGemma 4B is multimodal (uses a processor); text-only variants use a
    # tokenizer. Try the tokenizer path first, fall back to the processor.
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
        processor = None
    except Exception:  # pragma: no cover - depends on model variant
        processor = AutoProcessor.from_pretrained(model_id, token=token)
        tokenizer = processor.tokenizer

    model = AutoModelForCausalLM.from_pretrained(
        model_id, torch_dtype=torch_dtype, device_map=device, token=token)
    model.eval()

    def _generate(prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        inputs = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt",
            return_dict=True).to(model.device)
        input_len = inputs["input_ids"].shape[-1]
        import torch as _torch
        with _torch.no_grad():
            out = model.generate(
                **inputs, max_new_tokens=max_new_tokens,
                do_sample=False, temperature=None, top_p=None, top_k=None)
        gen = out[0][input_len:]
        return tokenizer.decode(gen, skip_special_tokens=True)

    return _generate


def build_medgemma_extractor(model_id: str = DEFAULT_MODEL,
                             **kwargs) -> Callable[[str], Dict[str, bool]]:
    """Convenience: load MedGemma and return the note->feature extractor."""
    return build_extractor_from_generate(load_medgemma(model_id, **kwargs))


# --------------------------------------------------------------------------- #
# Deterministic scripted stand-in (NO model) for end-to-end harness validation.
# It emits schema JSON exactly as a well-behaved LLM would, so the parse ->
# schema_to_features -> safety -> metrics path is exercised without weights.
# This is a self-test utility, never reported as a model result.
# --------------------------------------------------------------------------- #
class ScriptedGenerator:
    """Return schema JSON for a note from lightweight, transparent cues.

    This is intentionally NOT the benchmark's cue set: it is a minimal, generic
    reader used only to prove the JSON/adapter/safety plumbing is correct and to
    exercise fence/prose-wrapped output parsing. It is *not* an extractor under
    test and its numbers are never published.
    """

    def __init__(self, wrap_fence: bool = True, add_prose: bool = True):
        self.wrap_fence = wrap_fence
        self.add_prose = add_prose

    def _read(self, note: str) -> Dict[str, str]:
        t = note.lower()

        def has(*subs: str) -> bool:
            return any(s in t for s in subs)

        laterality = "unknown"
        if has("bilateral", "both ears", "both sides"):
            laterality = "bilateral"
        elif has("right ear", "on the right", "right-sided", "right side"):
            laterality = "right"
        elif has("left ear", "on the left", "left-sided", "left side", "one side",
                 "one ear"):
            laterality = "left"

        course = "unknown"
        if has("sudden", "overnight", "this morning", "since yesterday",
               "woke up", "went dead", "cut out", "stopped working"):
            course = "sudden"
        elif has("rapidly progressive", "progressive", "over the past few days",
                 "over days", "faded quickly", "over a couple of days"):
            course = "rapidly_progressive"
        elif has("gradual", "years", "long-standing", "chronic", "age-related"):
            course = "gradual"

        historical = has("history of", "years ago", "resolved", "recovered",
                         "used to")
        if historical:
            course = "gradual"

        def yn(cond: bool) -> str:
            return "yes" if cond else "no"

        return {
            "symptom_onset_date": "unknown",
            "laterality": laterality,
            "course": course,
            "tinnitus_present": yn(has("tinnitus", "ringing")),
            "hearing_loss_reported": yn(has("hearing", "hear", "deaf", "loss",
                                            "muffled")),
            "audiometric_asymmetry": yn(has("asymmetr", "lopsided", "worse on")),
            "ear_fullness": yn(has("fullness", "blocked", "plugged", "feels full")),
            "vertigo": yn(has("vertigo", "spinning", "dizzy")),
            "neurologic_red_flag": yn(has("facial weakness", "neurologic",
                                          "numbness", "diplopia")),
            "first_audiogram_date": "unknown",
            "treatment_date": "unknown",
            "noise_exposure": "unknown",
        }

    def __call__(self, prompt: str) -> str:
        # The prompt embeds the clinical note after the schema; recover it.
        note = prompt.split("Clinical note:")[-1].strip()
        payload = json.dumps(self._read(note), ensure_ascii=False)
        if self.wrap_fence:
            body = f"```json\n{payload}\n```"
        else:
            body = payload
        if self.add_prose:
            return ("Here is the extracted structured record.\n" + body +
                    "\nThis is not a diagnosis; clinician review required.")
        return body


def scripted_extractor(**kwargs) -> Callable[[str], Dict[str, bool]]:
    """Extractor backed by ``ScriptedGenerator`` (harness self-test only)."""
    return build_extractor_from_generate(ScriptedGenerator(**kwargs))
