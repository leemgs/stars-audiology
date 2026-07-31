"""Deterministic red-flag safety layer for HEAR-WORK AI.

This module implements the guideline-derived safety rules described in the
manuscript (Section: Open AI System). It is intentionally *deterministic* and
independent of any probabilistic model: a red flag always forces an urgent
referral message and overrides model output. A low predicted risk must never
suppress time-critical referral for sudden sensorineural hearing loss (SSNHL)
or neurologic warning signs.

References:
- Chandrasekhar et al. (2019), Clinical practice guideline: Sudden hearing loss.
- Tunkel et al. (2014), Clinical practice guideline: Tinnitus.

The rules are conservative by design; the evaluation metric of interest is
recall (a missed red flag is the costly error).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

URGENT_REFERRAL = (
    "URGENT: features suggestive of a time-critical otologic condition were "
    "detected. Recommend same-day audiometry and otolaryngology evaluation. "
    "This is not a diagnosis."
)
ROUTINE_MESSAGE = (
    "No red-flag features detected by the deterministic safety layer. "
    "Probabilistic model output may be shown for research purposes only; "
    "it is not a diagnosis and does not replace clinical assessment."
)


@dataclass
class RedFlagResult:
    urgent: bool
    triggered_rules: List[str] = field(default_factory=list)
    message: str = ""


# Each rule maps a canonical name to the boolean field(s) that trigger it.
RED_FLAG_RULES = {
    "sudden_hearing_loss": ("sudden_hearing_loss",),
    "rapidly_progressive_loss": ("rapidly_progressive_loss",),
    "unilateral_sudden_symptom": ("unilateral_sudden_symptom",),
    "aural_fullness_acute_onset": ("aural_fullness_acute_onset",),
    "single_sided_tinnitus_asymmetry": ("single_sided_tinnitus", "asymmetric_hearing"),
    "vertigo": ("vertigo",),
    "focal_neurologic_sign": ("focal_neurologic_sign",),
}


def evaluate_red_flags(features: dict) -> RedFlagResult:
    """Evaluate deterministic red-flag rules against a feature dict.

    Parameters
    ----------
    features: dict of boolean-like indicators. Missing keys are treated as False.

    Returns
    -------
    RedFlagResult with the urgent decision, the list of triggered rules, and a
    patient-safe message. The decision is a logical OR across rules; combined
    rules (tuples) require all listed indicators to be truthy.
    """
    triggered: List[str] = []
    for rule_name, required in RED_FLAG_RULES.items():
        if all(bool(features.get(key, False)) for key in required):
            triggered.append(rule_name)
    urgent = len(triggered) > 0
    return RedFlagResult(
        urgent=urgent,
        triggered_rules=triggered,
        message=URGENT_REFERRAL if urgent else ROUTINE_MESSAGE,
    )


def gate_model_output(features: dict, model_message: str) -> str:
    """Return the safe message: the red-flag layer overrides model output."""
    result = evaluate_red_flags(features)
    if result.urgent:
        return result.message
    return model_message
