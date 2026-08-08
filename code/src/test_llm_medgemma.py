"""End-to-end validation of the open medical-LLM (MedGemma) extractor path
WITHOUT model weights.

These tests exercise the exact production code path an actual MedGemma call would
take -- prompt build -> raw generation -> robust JSON parse (fences + prose) ->
schema_to_features -> deterministic safety layer -> metrics -- using a scripted
generator in place of the model. They prove the plumbing (not the model) is
correct, so the only remaining requirement for a real MedGemma number is model
access, not code.

Run:  python src/test_llm_medgemma.py   (plain asserts; also pytest-compatible)
"""
from __future__ import annotations

import json

from llm_extract import EXTRACTION_SCHEMA, extract_with_prompt_template
from llm_medgemma import (
    ScriptedGenerator,
    build_extractor_from_generate,
    robust_parse_fields,
    scripted_extractor,
)
from redflag_benchmark import FEATURE_KEYS, TEXT_CASES, schema_to_features
from safety import evaluate_red_flags


def test_robust_parse_handles_fences_and_prose():
    payload = {k: "unknown" for k in EXTRACTION_SCHEMA}
    payload["laterality"] = "right"
    payload["course"] = "sudden"
    payload["hearing_loss_reported"] = "yes"
    raw = ("Sure, here is the record:\n```json\n" + json.dumps(payload) +
           "\n```\nRemember, clinician review is required.")
    fields = robust_parse_fields(raw)
    assert fields["laterality"] == "right"
    assert fields["course"] == "sudden"
    # every schema key is present (missing -> unknown), so mapping never KeyErrors
    assert set(EXTRACTION_SCHEMA).issubset(fields)


def test_robust_parse_bad_output_is_conservative():
    fields = robust_parse_fields("the model refused and produced no json")
    assert all(fields[k] == "unknown" for k in EXTRACTION_SCHEMA)
    feats = schema_to_features(fields)
    # all-unknown must map to no red flag (safe/conservative default)
    assert not any(feats.values())
    assert evaluate_red_flags(feats).urgent is False


def test_schema_now_carries_asymmetry_and_progressive():
    # the two inputs the earlier schema omitted are now honored end to end
    fields = {k: "unknown" for k in EXTRACTION_SCHEMA}
    fields.update(audiometric_asymmetry="yes", tinnitus_present="yes",
                  laterality="left")
    feats = schema_to_features(fields)
    assert feats["asymmetric_hearing"] is True
    assert feats["single_sided_tinnitus"] is True
    # single-sided tinnitus WITH asymmetry is a guideline red flag
    assert evaluate_red_flags(feats).urgent is True

    fields2 = {k: "unknown" for k in EXTRACTION_SCHEMA}
    fields2.update(course="rapidly_progressive", laterality="right",
                   hearing_loss_reported="yes")
    feats2 = schema_to_features(fields2)
    assert feats2["rapidly_progressive_loss"] is True
    assert feats2["unilateral_sudden_symptom"] is True
    assert evaluate_red_flags(feats2).urgent is True


def test_scripted_generator_emits_valid_schema_json():
    gen = ScriptedGenerator()
    prompt = extract_with_prompt_template(
        "Sudden hearing loss in the right ear since yesterday with fullness.")
    raw = gen(prompt)
    fields = robust_parse_fields(raw)
    assert fields["course"] == "sudden"
    assert fields["laterality"] == "right"
    assert fields["ear_fullness"] == "yes"


def test_full_path_flags_urgent_case():
    extract = scripted_extractor()
    feats = extract("Sudden hearing loss in the right ear since yesterday.")
    assert feats["sudden_hearing_loss"] is True
    assert evaluate_red_flags(feats).urgent is True


def test_full_path_does_not_flag_benign_case():
    extract = scripted_extractor()
    feats = extract("Chronic bilateral tinnitus associated with stress; hearing "
                    "stable for years.")
    assert evaluate_red_flags(feats).urgent is False


def test_extractor_runs_over_whole_benchmark():
    # the LLM-style extractor must produce the full feature dict for every note,
    # so the unified runner can score it exactly like the rule-based extractors
    extract = build_extractor_from_generate(ScriptedGenerator())
    for case in TEXT_CASES:
        feats = extract(case.note)
        assert set(feats) == set(FEATURE_KEYS)
        assert all(isinstance(v, bool) for v in feats.values())


def _run_all():
    import inspect
    mod = globals()
    tests = [v for k, v in mod.items() if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        t()
        passed += 1
        print(f"  ok  {t.__name__}")
    print(f"{passed}/{len(tests)} tests passed")


if __name__ == "__main__":
    _run_all()
