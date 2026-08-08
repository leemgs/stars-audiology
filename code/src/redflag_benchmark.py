"""Open benchmark for the STARS referral-safety layer and schema extraction.

This is the evaluation corpus for the *companion* (paper B) study: a
deterministic, guideline-derived red-flag layer that gates an open medical-LLM
extraction front-end for time-critical otologic symptoms (SSNHL / neurologic
warning signs). It contains NO patient data: every case is expert-authored or
synthetic, so the benchmark can be released and re-run openly.

Two evaluation levels are supported (see run_redflag_eval.py):

1. STRUCTURED level -- gold urgency (defined a priori by the SSNHL/tinnitus
   guidelines, *independently* of the rule code) vs. the deterministic layer
   applied to correctly-extracted features. This measures **rule coverage**:
   does the rule set flag every guideline red flag and avoid over-flagging
   benign presentations?

2. END-TO-END level -- natural-language notes are run through a schema-
   constrained rule-based extractor (extract_features) and then the safety
   layer. Adversarial notes (negation, colloquial, ambiguous onset) make the
   extractor err, so end-to-end recall/specificity are bounded by extraction --
   the honest, non-trivial result that motivates mandatory clinician review.

The same TEXT_CASES also drive the field-level extraction metrics
(run_extraction_eval.py) against gold structured fields.

Feature keys match safety.RED_FLAG_RULES:
  sudden_hearing_loss, rapidly_progressive_loss, unilateral_sudden_symptom,
  aural_fullness_acute_onset, single_sided_tinnitus, asymmetric_hearing,
  vertigo, focal_neurologic_sign
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

FEATURE_KEYS = [
    "sudden_hearing_loss", "rapidly_progressive_loss", "unilateral_sudden_symptom",
    "aural_fullness_acute_onset", "single_sided_tinnitus", "asymmetric_hearing",
    "vertigo", "focal_neurologic_sign",
]


@dataclass
class Structured:
    desc: str
    features: Dict[str, bool]
    gold_urgent: bool           # a priori guideline label (NOT the rule output)
    source: str                 # expert | synthetic
    laterality: Optional[str] = None   # unilateral | bilateral
    onset: Optional[str] = None        # acute | gradual
    vertigo_neuro: bool = False


@dataclass
class TextCase:
    note: str
    gold_features: Dict[str, bool]
    gold_urgent: bool
    category: str               # typical | negation | colloquial | ambiguous
    source: str = "expert"
    laterality: Optional[str] = None
    onset: Optional[str] = None
    vertigo_neuro: bool = False


def _f(**kw) -> Dict[str, bool]:
    """Feature dict with all keys defaulted to False, overridden by kwargs."""
    d = {k: False for k in FEATURE_KEYS}
    d.update(kw)
    return d


# --------------------------------------------------------------------------- #
# STRUCTURED benchmark: gold urgency set a priori from the guidelines.
# Positives cover every red-flag rule; negatives probe over-referral (esp. the
# single-sided-tinnitus-WITHOUT-asymmetry case, which must NOT be flagged).
# --------------------------------------------------------------------------- #
STRUCTURED: List[Structured] = [
    # --- urgent (guideline red flags) ---
    Structured("Sudden unilateral SNHL with acute aural fullness",
               _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                  aural_fullness_acute_onset=True), True, "expert", "unilateral", "acute"),
    Structured("Sudden unilateral SNHL, no fullness",
               _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True),
               True, "expert", "unilateral", "acute"),
    Structured("Rapidly progressive unilateral loss over days",
               _f(rapidly_progressive_loss=True, unilateral_sudden_symptom=True),
               True, "expert", "unilateral", "acute"),
    Structured("Rapidly progressive bilateral loss over 2 weeks",
               _f(rapidly_progressive_loss=True), True, "expert", "bilateral", "acute"),
    Structured("Single-sided tinnitus WITH documented audiometric asymmetry",
               _f(single_sided_tinnitus=True, asymmetric_hearing=True),
               True, "expert", "unilateral", "gradual"),
    Structured("Acute vertigo with unilateral hearing change",
               _f(vertigo=True, unilateral_sudden_symptom=True), True,
               "expert", "unilateral", "acute", vertigo_neuro=True),
    Structured("Focal neurologic sign (facial weakness) with hearing complaint",
               _f(focal_neurologic_sign=True), True, "expert", None, None, True),
    Structured("Sudden bilateral loss (rare, urgent)",
               _f(sudden_hearing_loss=True), True, "synthetic", "bilateral", "acute"),
    Structured("Acute aural fullness with sudden drop, unilateral",
               _f(aural_fullness_acute_onset=True, sudden_hearing_loss=True,
                  unilateral_sudden_symptom=True), True, "synthetic", "unilateral", "acute"),
    Structured("Vertigo + focal neurologic sign (central concern)",
               _f(vertigo=True, focal_neurologic_sign=True), True, "expert",
               None, "acute", True),
    Structured("Single-sided tinnitus with asymmetry and fullness",
               _f(single_sided_tinnitus=True, asymmetric_hearing=True,
                  aural_fullness_acute_onset=True), True, "synthetic", "unilateral", "acute"),
    Structured("Rapidly progressive unilateral loss with tinnitus asymmetry",
               _f(rapidly_progressive_loss=True, single_sided_tinnitus=True,
                  asymmetric_hearing=True), True, "synthetic", "unilateral", "acute"),
    # --- non-urgent (benign / chronic; must NOT be flagged) ---
    Structured("Chronic bilateral stress-associated tinnitus, stable hearing",
               _f(), False, "expert", "bilateral", "gradual"),
    Structured("Long-standing symmetric high-frequency loss, noise history",
               _f(), False, "expert", "bilateral", "gradual"),
    Structured("Single-sided tinnitus WITHOUT asymmetry (combined rule not met)",
               _f(single_sided_tinnitus=True, asymmetric_hearing=False),
               False, "expert", "unilateral", "gradual"),
    Structured("Gradual symmetric age-related loss",
               _f(), False, "synthetic", "bilateral", "gradual"),
    Structured("Bilateral tinnitus after a concert, resolving, symmetric hearing",
               _f(), False, "synthetic", "bilateral", "acute"),
    Structured("Mild gradual unilateral loss, no sudden change, no asymmetry flag",
               _f(), False, "expert", "unilateral", "gradual"),
    Structured("Stable asymmetry known for years, no new symptom",
               _f(asymmetric_hearing=True), False, "expert", "unilateral", "gradual"),
    Structured("Cerumen-related muffled hearing, gradual, bilateral",
               _f(), False, "synthetic", "bilateral", "gradual"),
    # --- expansion: more urgent ---
    Structured("Sudden unilateral loss with same-day tinnitus onset",
               _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                  single_sided_tinnitus=True, asymmetric_hearing=True), True,
               "expert", "unilateral", "acute"),
    Structured("Fluctuating loss with recurrent vertigo (Meniere-like)",
               _f(vertigo=True), True, "expert", "unilateral", "acute", vertigo_neuro=True),
    Structured("Unilateral tinnitus with asymmetry and acute vertigo",
               _f(single_sided_tinnitus=True, asymmetric_hearing=True, vertigo=True),
               True, "synthetic", "unilateral", "acute", vertigo_neuro=True),
    Structured("Rapidly progressive bilateral loss with a focal neurologic sign",
               _f(rapidly_progressive_loss=True, focal_neurologic_sign=True), True,
               "expert", "bilateral", "acute", vertigo_neuro=True),
    Structured("Sudden unilateral loss after an upper-respiratory infection",
               _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True), True,
               "synthetic", "unilateral", "acute"),
    Structured("Acute unilateral fullness with sudden drop and tinnitus",
               _f(aural_fullness_acute_onset=True, sudden_hearing_loss=True,
                  unilateral_sudden_symptom=True, single_sided_tinnitus=True,
                  asymmetric_hearing=True), True, "synthetic", "unilateral", "acute"),
    Structured("Sudden bilateral loss with vertigo",
               _f(sudden_hearing_loss=True, vertigo=True), True, "expert",
               "bilateral", "acute", vertigo_neuro=True),
    # --- expansion: more benign (must NOT flag) ---
    Structured("Bilateral symmetric noise-induced loss, stable for years",
               _f(), False, "expert", "bilateral", "gradual"),
    Structured("Chronic unilateral tinnitus with a symmetric audiogram",
               _f(single_sided_tinnitus=True, asymmetric_hearing=False), False,
               "expert", "unilateral", "gradual"),
    Structured("Gradual bilateral presbycusis",
               _f(), False, "synthetic", "bilateral", "gradual"),
    Structured("Resolved otitis media, hearing recovered, conductive picture",
               _f(), False, "expert", "unilateral", "gradual"),
    Structured("Bilateral tinnitus with a normal audiogram, anxiety context",
               _f(), False, "synthetic", "bilateral", "gradual"),
    Structured("Bilateral wax impaction, gradual muffling",
               _f(), False, "synthetic", "bilateral", "gradual"),
    Structured("Long-known stable asymmetry, no new or sudden symptom",
               _f(asymmetric_hearing=True), False, "expert", "unilateral", "gradual"),
]


# --------------------------------------------------------------------------- #
# TEXT benchmark: natural-language notes with gold features + gold urgency.
# Categories: typical (clean), negation (explicit negatives), colloquial (lay
# phrasing), ambiguous (vague onset/laterality). These drive BOTH end-to-end
# safety and field-level extraction metrics.
# --------------------------------------------------------------------------- #
TEXT_CASES: List[TextCase] = [
    # ---- typical positives ----
    TextCase("Patient reports sudden hearing loss in the right ear since yesterday "
             "with a feeling of fullness.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                aural_fullness_acute_onset=True), True, "typical",
             laterality="unilateral", onset="acute"),
    TextCase("Left-sided tinnitus with an audiogram showing asymmetric "
             "sensorineural loss on the left.",
             _f(single_sided_tinnitus=True, asymmetric_hearing=True), True,
             "typical", laterality="unilateral", onset="gradual"),
    TextCase("Rapidly progressive hearing loss over the past few days with "
             "unilateral onset.",
             _f(rapidly_progressive_loss=True, unilateral_sudden_symptom=True),
             True, "typical", laterality="unilateral", onset="acute"),
    TextCase("Acute vertigo and a sudden change in hearing on the right.",
             _f(vertigo=True, unilateral_sudden_symptom=True), True, "typical",
             laterality="unilateral", onset="acute", vertigo_neuro=True),
    TextCase("Facial weakness noted alongside a new hearing complaint; neurologic "
             "concern.",
             _f(focal_neurologic_sign=True), True, "typical", vertigo_neuro=True),
    # ---- typical negatives ----
    TextCase("Chronic bilateral tinnitus associated with stress; hearing has been "
             "stable for years.",
             _f(), False, "typical", laterality="bilateral", onset="gradual"),
    TextCase("Gradual, symmetric high-frequency hearing loss consistent with age "
             "and prior noise exposure.",
             _f(), False, "typical", laterality="bilateral", onset="gradual"),
    TextCase("Single-sided tinnitus but the audiogram is symmetric with no "
             "asymmetry.",
             _f(single_sided_tinnitus=True, asymmetric_hearing=False), False,
             "typical", laterality="unilateral", onset="gradual"),
    # ---- negation (extractor is prone to false alarms here) ----
    TextCase("No sudden hearing loss; the patient denies any acute change or "
             "vertigo.",
             _f(), False, "negation", laterality="bilateral", onset="gradual"),
    TextCase("Denies facial weakness or other neurologic symptoms; long-standing "
             "tinnitus only.",
             _f(), False, "negation", onset="gradual"),
    TextCase("There is no aural fullness and no sudden drop in hearing.",
             _f(), False, "negation", onset="gradual"),
    TextCase("Reports tinnitus but explicitly no asymmetry on testing.",
             _f(single_sided_tinnitus=True, asymmetric_hearing=False), False,
             "negation", laterality="unilateral", onset="gradual"),
    # ---- colloquial (extractor is prone to misses here) ----
    TextCase("Woke up and my good ear went dead overnight, feels blocked.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                aural_fullness_acute_onset=True), True, "colloquial",
             laterality="unilateral", onset="acute"),
    TextCase("The room was spinning and my hearing dropped out on one side.",
             _f(vertigo=True, unilateral_sudden_symptom=True), True, "colloquial",
             laterality="unilateral", onset="acute", vertigo_neuro=True),
    TextCase("Ringing only in the left and the hearing test came back lopsided.",
             _f(single_sided_tinnitus=True, asymmetric_hearing=True), True,
             "colloquial", laterality="unilateral", onset="gradual"),
    TextCase("Just the usual ringing in both ears, nothing new.",
             _f(), False, "colloquial", laterality="bilateral", onset="gradual"),
    # ---- ambiguous (vague timing/side) ----
    TextCase("Some hearing change recently, not sure which ear or how fast.",
             _f(), False, "ambiguous", onset="gradual"),
    TextCase("Progressive loss; unclear if over days or months, right worse.",
             _f(rapidly_progressive_loss=True, unilateral_sudden_symptom=True),
             True, "ambiguous", laterality="unilateral", onset="acute"),
    # ---- hard cases: urgent presentations WITHOUT canonical keywords (a simple
    #      extractor is expected to miss these -> realistic end-to-end recall gap) ----
    TextCase("After the flight my right ear stopped working and won't come back.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True), True,
             "colloquial", laterality="unilateral", onset="acute"),
    TextCase("Over the last two days the hearing in one ear has faded quickly.",
             _f(rapidly_progressive_loss=True, unilateral_sudden_symptom=True), True,
             "ambiguous", laterality="unilateral", onset="acute"),
    # ---- hard negative: a resolved historical event that keyword matching may
    #      false-alarm on (temporal context) ----
    TextCase("History of sudden hearing loss ten years ago, fully recovered; now "
             "only stable chronic tinnitus.",
             _f(), False, "ambiguous", laterality="bilateral", onset="gradual"),
    # ---- expansion: typical ----
    TextCase("Sudden right-sided hearing loss since this morning with tinnitus.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                single_sided_tinnitus=True), True, "typical",
             laterality="unilateral", onset="acute"),
    TextCase("New left-ear hearing drop over the past day with fullness.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                aural_fullness_acute_onset=True), True, "typical",
             laterality="unilateral", onset="acute"),
    TextCase("Vertigo with a sudden decline in hearing on the left.",
             _f(vertigo=True, sudden_hearing_loss=True, unilateral_sudden_symptom=True),
             True, "typical", laterality="unilateral", onset="acute", vertigo_neuro=True),
    TextCase("Stable symmetric hearing loss from years of factory noise.",
             _f(), False, "typical", laterality="bilateral", onset="gradual"),
    TextCase("Bilateral ringing, audiogram symmetric, no change.",
             _f(), False, "typical", laterality="bilateral", onset="gradual"),
    TextCase("Gradual age-related hearing decline in both ears.",
             _f(), False, "typical", laterality="bilateral", onset="gradual"),
    # ---- expansion: negation ----
    TextCase("No vertigo and no sudden loss; chronic bilateral tinnitus only.",
             _f(), False, "negation", laterality="bilateral", onset="gradual"),
    TextCase("Patient denies any sudden change or facial weakness.",
             _f(), False, "negation", onset="gradual"),
    TextCase("No asymmetry on the audiogram; bilateral tinnitus.",
             _f(), False, "negation", laterality="bilateral", onset="gradual"),
    # ---- expansion: colloquial (v1 prone to misses) ----
    TextCase("One ear conked out this morning and feels plugged.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True,
                aural_fullness_acute_onset=True), True, "colloquial",
             laterality="unilateral", onset="acute"),
    TextCase("Everything went muffled on the right after I got off the plane.",
             _f(sudden_hearing_loss=True, unilateral_sudden_symptom=True), True,
             "colloquial", laterality="unilateral", onset="acute"),
    TextCase("My ears ring all the time, same as always.",
             _f(), False, "colloquial", laterality="bilateral", onset="gradual"),
    TextCase("Felt dizzy and my hearing cut out on one side.",
             _f(vertigo=True, unilateral_sudden_symptom=True, sudden_hearing_loss=True),
             True, "colloquial", laterality="unilateral", onset="acute", vertigo_neuro=True),
    # ---- expansion: ambiguous (v1 prone to misses/false-alarms) ----
    TextCase("Progressive drop over a couple of days, right side worse.",
             _f(rapidly_progressive_loss=True, unilateral_sudden_symptom=True), True,
             "ambiguous", laterality="unilateral", onset="acute"),
    TextCase("Some hearing trouble lately, both ears, nothing sudden.",
             _f(), False, "ambiguous", laterality="bilateral", onset="gradual"),
    TextCase("History of a sudden loss years ago, resolved; now stable tinnitus.",
             _f(), False, "ambiguous", laterality="bilateral", onset="gradual"),
]


# --------------------------------------------------------------------------- #
# Schema-constrained RULE-BASED extractor (open, deterministic reference).
# This is the reproducible baseline that an open medical LLM (e.g., MedGemma)
# will be benchmarked against once model + clinical-text access are available.
# It intentionally uses simple cues + a short negation window, so its failures
# on adversarial phrasing are realistic and informative.
# --------------------------------------------------------------------------- #
_NEG = re.compile(r"\b(no|not|nothing|none|denies|denied|without|negative for)\b")


def _norm(s: str) -> str:
    """Lowercase and collapse to [a-z'] tokens so hyphenation/punctuation do not
    defeat cue matching (e.g., 'left-sided' == 'left sided')."""
    return " ".join(re.findall(r"[a-z']+", s.lower()))


def _present(text: str, cues: List[str], neg_window: int = 5) -> bool:
    """True if any cue appears and is not preceded by a negation within a short
    word window (a deliberately simple heuristic). Both text and cues are
    normalized so surface punctuation does not cause spurious misses."""
    joined = _norm(text)
    for cue in cues:
        c = _norm(cue)
        idx = joined.find(c)
        if idx == -1:
            continue
        bw = joined[:idx].split()[-neg_window:]
        if not _NEG.search(" " + " ".join(bw) + " "):
            return True
    return False


def extract_features(text: str) -> Dict[str, bool]:
    """Extract the safety feature flags from free text (rule-based baseline)."""
    t = text.lower()
    sudden = _present(t, ["sudden hearing", "sudden loss", "sudden drop",
                          "sudden change", "went dead", "dropped out"])
    rapid = _present(t, ["rapidly progressive", "progressive hearing",
                         "progressive loss", "over the past few days", "over days"])
    unilateral_acute = _present(
        t, ["right ear", "left ear", "one side", "unilateral", "on the right",
            "on the left", "right worse", "left worse"]) and (
        sudden or rapid or _present(t, ["vertigo", "spinning"]))
    fullness = _present(t, ["fullness", "blocked", "feels full"])
    single_tinnitus = _present(
        t, ["left-sided tinnitus", "right-sided tinnitus", "single-sided tinnitus",
            "tinnitus only in", "ringing only in the left",
            "ringing only in the right", "one-sided tinnitus"])
    asymmetry = _present(t, ["asymmetric", "asymmetry", "lopsided", "worse on"])
    vertigo = _present(t, ["vertigo", "spinning", "room was spinning"])
    neuro = _present(t, ["facial weakness", "neurologic", "focal", "diplopia",
                         "numbness"])
    return {
        "sudden_hearing_loss": sudden,
        "rapidly_progressive_loss": rapid,
        "unilateral_sudden_symptom": unilateral_acute,
        "aural_fullness_acute_onset": fullness and (sudden or rapid),
        "single_sided_tinnitus": single_tinnitus,
        "asymmetric_hearing": asymmetry,
        "vertigo": vertigo,
        "focal_neurologic_sign": neuro,
    }


_HIST = re.compile(
    r"\b(history of|years ago|ten years ago|in the past|previously|"
    r"resolved|fully recovered|recovered|used to)\b")


def extract_features_v2(text: str) -> Dict[str, bool]:
    """Improved rule-based extractor: adds colloquial/implicit cues and suppresses
    red flags stated in a HISTORICAL/RESOLVED context. Demonstrates that the open
    benchmark discriminates extractor quality (v2 should beat extract_features).
    """
    t = text.lower()
    historical = bool(_HIST.search(_norm(t)))
    sudden = _present(t, ["sudden hearing", "sudden loss", "sudden drop",
                          "sudden change", "sudden decline", "went dead",
                          "dropped out", "conked out", "cut out", "went out",
                          "stopped working", "quit working", "went muffled",
                          "hearing drop", "hearing cut"])
    # Co-occurrence: "sudden(ly)" together with a hearing/loss term even when
    # separated by intervening words (e.g., "sudden right-sided hearing loss").
    if not sudden and _present(t, ["sudden", "suddenly"]) and \
            _present(t, ["hearing", "hear", "loss", "deaf", "ear"]):
        sudden = True
    rapid = _present(t, ["rapidly progressive", "progressive hearing",
                         "progressive loss", "progressive drop", "faded quickly",
                         "over the past few days", "over days",
                         "over a couple of days", "over the past day"])
    # Historical/resolved events are not ACTIVE red flags.
    if historical:
        sudden = rapid = False
    lat = _present(t, ["right ear", "left ear", "one side", "one ear", "unilateral",
                       "on the right", "on the left", "right worse", "left worse",
                       "right side", "left side", "right-sided", "left-sided",
                       "on one side"])
    vertigo = _present(t, ["vertigo", "spinning", "room was spinning", "dizzy",
                           "dizziness"])
    unilateral_acute = lat and (sudden or rapid or vertigo)
    fullness = _present(t, ["fullness", "blocked", "feels full", "plugged"])
    single_tinnitus = _present(
        t, ["left-sided tinnitus", "right-sided tinnitus", "single-sided tinnitus",
            "tinnitus only in", "ringing only in the left",
            "ringing only in the right", "one-sided tinnitus", "tinnitus on the left",
            "tinnitus on the right"])
    asymmetry = _present(t, ["asymmetric", "asymmetry", "lopsided", "worse on"])
    neuro = _present(t, ["facial weakness", "neurologic", "focal", "diplopia",
                         "numbness"])
    return {
        "sudden_hearing_loss": sudden,
        "rapidly_progressive_loss": rapid,
        "unilateral_sudden_symptom": unilateral_acute,
        "aural_fullness_acute_onset": fullness and (sudden or rapid),
        "single_sided_tinnitus": single_tinnitus,
        "asymmetric_hearing": asymmetry,
        "vertigo": vertigo,
        "focal_neurologic_sign": neuro,
    }


def schema_to_features(fields: Dict[str, str]) -> Dict[str, bool]:
    """Map an LLM schema extraction (llm_extract.EXTRACTION_SCHEMA fields) to the
    safety feature flags, so an open medical LLM (e.g., MedGemma) plugs into the
    SAME harness once model access is available.

    The extraction schema now carries the two red-flag inputs the earlier version
    omitted -- audiometric ``asymmetry`` and a ``rapidly_progressive`` course --
    so an LLM mapped through this adapter no longer inherits those blind spots.
    Unknown/missing fields still map conservatively (to False), which keeps the
    mapping safe by construction: a rule can only fire on an affirmative field.
    """
    def yes(k):
        return str(fields.get(k, "")).lower() == "yes"
    course = str(fields.get("course", "")).lower()
    lat = str(fields.get("laterality", "")).lower()
    unilateral = lat in ("left", "right")
    sudden = course == "sudden" and yes("hearing_loss_reported")
    rapid = course in ("rapidly_progressive", "progressive")
    acute = sudden or rapid
    return {
        "sudden_hearing_loss": sudden,
        "rapidly_progressive_loss": rapid,
        "unilateral_sudden_symptom": unilateral and acute,
        "aural_fullness_acute_onset": yes("ear_fullness") and acute,
        "single_sided_tinnitus": yes("tinnitus_present") and unilateral,
        "asymmetric_hearing": yes("audiometric_asymmetry"),
        "vertigo": yes("vertigo"),
        "focal_neurologic_sign": yes("neurologic_red_flag"),
    }


def make_llm_extractor(generate):
    """Build an extractor from a text-generation callable ``generate(prompt)->str``
    (e.g., a local MedGemma). Prospective: register in EXTRACTORS when a model is
    available. Kept here so the evaluation path is concrete and prespecified."""
    from llm_extract import extract_with_prompt_template, parse_llm_json

    def _extract(text: str) -> Dict[str, bool]:
        raw = generate(extract_with_prompt_template(text))
        return schema_to_features(parse_llm_json(raw).fields)
    return _extract


# Registry of the open, deterministic rule-based references. An open medical LLM
# (MedGemma) is evaluated through the SAME harness via run_llm_eval.py, which
# builds its extractor with llm_medgemma.build_medgemma_extractor and scores it
# against this identical benchmark/adapter. It is not registered here because the
# model is a gated, GPU-dependent download; run_llm_eval.py loads it on demand.
EXTRACTORS = {
    "rule_v1": extract_features,
    "rule_v2": extract_features_v2,
}


def benchmark_summary() -> dict:
    return {
        "n_structured": len(STRUCTURED),
        "structured_urgent": sum(s.gold_urgent for s in STRUCTURED),
        "n_text": len(TEXT_CASES),
        "text_urgent": sum(t.gold_urgent for t in TEXT_CASES),
        "text_categories": sorted({t.category for t in TEXT_CASES}),
    }
