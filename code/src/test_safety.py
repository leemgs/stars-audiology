"""Red-flag vignette test suite for the deterministic safety layer.

Run: python -m pytest src/test_safety.py   (or: python src/test_safety.py)

The curated vignettes below mix red-flag and non-red-flag cases. The primary
metric reported in the manuscript is recall on red-flag cases, which must be
1.0 (no missed red flag).
"""
from __future__ import annotations

from safety import evaluate_red_flags, gate_model_output, URGENT_REFERRAL

# (description, features, expected_urgent)
VIGNETTES = [
    ("SSNHL: sudden unilateral loss with fullness",
     {"sudden_hearing_loss": True, "unilateral_sudden_symptom": True,
      "aural_fullness_acute_onset": True}, True),
    ("Rapidly progressive loss over days",
     {"rapidly_progressive_loss": True}, True),
    ("Single-sided tinnitus with asymmetry",
     {"single_sided_tinnitus": True, "asymmetric_hearing": True}, True),
    ("Vertigo with hearing change",
     {"vertigo": True}, True),
    ("Focal neurologic sign",
     {"focal_neurologic_sign": True}, True),
    ("Chronic bilateral stress-associated tinnitus, stable hearing",
     {"single_sided_tinnitus": False, "asymmetric_hearing": False,
      "sudden_hearing_loss": False}, False),
    ("Long-standing symmetric high-frequency loss, noise history",
     {"asymmetric_hearing": False, "sudden_hearing_loss": False}, False),
    ("Single-sided tinnitus WITHOUT asymmetry (combined rule not met)",
     {"single_sided_tinnitus": True, "asymmetric_hearing": False}, False),
]


def test_red_flag_recall_is_perfect():
    positives = [v for v in VIGNETTES if v[2]]
    detected = [v for v in positives if evaluate_red_flags(v[1]).urgent]
    assert len(detected) == len(positives), "A red flag was missed (recall < 1.0)"


def test_no_false_alarm_on_clear_negatives():
    negatives = [v for v in VIGNETTES if not v[2]]
    for desc, feats, _ in negatives:
        assert not evaluate_red_flags(feats).urgent, f"False alarm on: {desc}"


def test_gate_overrides_model_on_red_flag():
    feats = {"sudden_hearing_loss": True}
    assert gate_model_output(feats, "model says low risk") == URGENT_REFERRAL


def _run_all():
    total = len(VIGNETTES)
    correct = sum(evaluate_red_flags(f).urgent == exp for _, f, exp in VIGNETTES)
    tp = sum(evaluate_red_flags(f).urgent and exp for _, f, exp in VIGNETTES)
    pos = sum(1 for _, _, exp in VIGNETTES if exp)
    print(f"Vignettes: {total}  Accuracy: {correct}/{total}  "
          f"Red-flag recall: {tp}/{pos} = {tp/pos:.2f}")
    for desc, feats, exp in VIGNETTES:
        r = evaluate_red_flags(feats)
        status = "OK" if r.urgent == exp else "FAIL"
        print(f"  [{status}] urgent={r.urgent} rules={r.triggered_rules} :: {desc}")


if __name__ == "__main__":
    _run_all()
