"""Red-flag safety-layer evaluation harness and unit tests.

Run: python -m pytest src/test_safety.py   (or: python src/test_safety.py)

This harness demonstrates the prespecified evaluation design (see manuscript
Table: red-flag evaluation plan). Each vignette carries composition metadata
(source type, laterality, onset, vertigo/neuro) so the harness can report
sensitivity (red-flag recall, the primary metric), specificity, over-referral
rate, and subgroup performance.

IMPORTANT: the deterministic layer operates on STRUCTURED boolean features.
Text-level robustness (negation, ambiguous time, colloquial phrasing) is the
responsibility of the upstream extraction step; a couple of illustrative
"parsed-negation" cases are included to show how a mis-parse would surface here.

A finite-set sensitivity of 1.00 is a TARGET, not a guarantee of zero misses in
deployment. This caveat is printed with every run and stated in the manuscript.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from safety import evaluate_red_flags, gate_model_output, URGENT_REFERRAL


@dataclass
class Vignette:
    desc: str
    features: dict
    expected_urgent: bool
    source: str            # real | expert | synthetic
    laterality: Optional[str] = None   # unilateral | bilateral | None
    onset: Optional[str] = None        # acute | gradual | None
    vertigo_neuro: bool = False


VIGNETTES = [
    Vignette("SSNHL: sudden unilateral loss with fullness",
             {"sudden_hearing_loss": True, "unilateral_sudden_symptom": True,
              "aural_fullness_acute_onset": True}, True, "real", "unilateral", "acute"),
    Vignette("Rapidly progressive unilateral loss over days",
             {"rapidly_progressive_loss": True, "unilateral_sudden_symptom": True},
             True, "real", "unilateral", "acute"),
    Vignette("Single-sided tinnitus with documented asymmetry",
             {"single_sided_tinnitus": True, "asymmetric_hearing": True},
             True, "expert", "unilateral", "gradual"),
    Vignette("Acute vertigo with hearing change",
             {"vertigo": True, "unilateral_sudden_symptom": True}, True,
             "expert", "unilateral", "acute", vertigo_neuro=True),
    Vignette("Focal neurologic sign with hearing complaint",
             {"focal_neurologic_sign": True}, True, "expert", None, None, True),
    Vignette("Sudden bilateral loss (rare but urgent)",
             {"sudden_hearing_loss": True}, True, "synthetic", "bilateral", "acute"),
    Vignette("Chronic bilateral stress-associated tinnitus, stable hearing",
             {"single_sided_tinnitus": False, "asymmetric_hearing": False,
              "sudden_hearing_loss": False}, False, "real", "bilateral", "gradual"),
    Vignette("Long-standing symmetric high-frequency loss, noise history",
             {"asymmetric_hearing": False, "sudden_hearing_loss": False},
             False, "real", "bilateral", "gradual"),
    Vignette("Single-sided tinnitus WITHOUT asymmetry (combined rule not met)",
             {"single_sided_tinnitus": True, "asymmetric_hearing": False},
             False, "expert", "unilateral", "gradual"),
    Vignette("Parsed-negation: 'no sudden loss' correctly parsed to False",
             {"sudden_hearing_loss": False}, False, "synthetic"),
    Vignette("Gradual symmetric age-related loss",
             {"sudden_hearing_loss": False, "asymmetric_hearing": False},
             False, "synthetic", "bilateral", "gradual"),
]


def _confusion():
    tp = fp = tn = fn = 0
    for v in VIGNETTES:
        pred = evaluate_red_flags(v.features).urgent
        if v.expected_urgent and pred:
            tp += 1
        elif v.expected_urgent and not pred:
            fn += 1
        elif not v.expected_urgent and pred:
            fp += 1
        else:
            tn += 1
    return tp, fp, tn, fn


# ---- unit tests -----------------------------------------------------------
def test_red_flag_recall_is_perfect():
    tp, _, _, fn = _confusion()
    assert fn == 0, "A red flag was missed (sensitivity < 1.0)"


def test_no_false_alarm_on_clear_negatives():
    _, fp, _, _ = _confusion()
    assert fp == 0, "False alarm on a clear negative vignette"


def test_gate_overrides_model_on_red_flag():
    assert gate_model_output({"sudden_hearing_loss": True}, "low risk") == URGENT_REFERRAL


# ---- reporting harness ----------------------------------------------------
def _rate(num, den):
    return float(num) / den if den else float("nan")


def _run_all():
    tp, fp, tn, fn = _confusion()
    sens = _rate(tp, tp + fn)
    spec = _rate(tn, tn + fp)
    over_referral = _rate(fp, fp + tn)
    print(f"Vignettes: {len(VIGNETTES)}  "
          f"(real={sum(v.source=='real' for v in VIGNETTES)}, "
          f"expert={sum(v.source=='expert' for v in VIGNETTES)}, "
          f"synthetic={sum(v.source=='synthetic' for v in VIGNETTES)})")
    print(f"Sensitivity (red-flag recall): {tp}/{tp+fn} = {sens:.2f}   "
          f"Specificity: {tn}/{tn+fp} = {spec:.2f}   "
          f"Over-referral: {over_referral:.2f}")
    # subgroup: acute vs gradual onset (positives only)
    for onset in ("acute", "gradual"):
        pos = [v for v in VIGNETTES if v.expected_urgent and v.onset == onset]
        hit = sum(evaluate_red_flags(v.features).urgent for v in pos)
        if pos:
            print(f"  onset={onset}: recall {hit}/{len(pos)}")
    print("CAVEAT: finite-set sensitivity of 1.00 is a target, NOT a guarantee "
          "of zero misses in deployment; the layer supplements, never replaces, "
          "clinical assessment.")
    for v in VIGNETTES:
        r = evaluate_red_flags(v.features)
        status = "OK" if r.urgent == v.expected_urgent else "FAIL"
        print(f"  [{status}] urgent={r.urgent} :: {v.desc}")


if __name__ == "__main__":
    _run_all()
