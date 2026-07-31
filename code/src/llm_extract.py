"""MedGemma-style schema-constrained clinical text extraction.

This module is disabled by default because clinical data require IRB approval,
local privacy review, and deidentification. It is included to make the future
hospital-cohort extension reproducible.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional


EXTRACTION_SCHEMA = {
    "symptom_onset_date": "YYYY-MM-DD or unknown",
    "laterality": "left/right/bilateral/unknown",
    "course": "sudden/gradual/fluctuating/unknown",
    "tinnitus_present": "yes/no/unknown",
    "hearing_loss_reported": "yes/no/unknown",
    "ear_fullness": "yes/no/unknown",
    "vertigo": "yes/no/unknown",
    "neurologic_red_flag": "yes/no/unknown",
    "first_audiogram_date": "YYYY-MM-DD or unknown",
    "treatment_date": "YYYY-MM-DD or unknown",
    "noise_exposure": "occupational/recreational/none/unknown",
}


@dataclass
class ExtractionResult:
    fields: Dict[str, str]
    requires_clinician_review: bool = True
    safety_flag: Optional[str] = None


def rule_based_red_flags(text: str) -> Optional[str]:
    lower = text.lower()
    if "sudden" in lower and ("hearing loss" in lower or "can't hear" in lower):
        return "sudden_hearing_loss_possible_urgent_referral"
    if "facial weakness" in lower or "neurologic" in lower:
        return "neurologic_red_flag"
    return None


def extract_with_prompt_template(note_text: str) -> str:
    """Return a prompt that can be passed to a local MedGemma model."""
    return f"""
You are extracting structured fields for an audiology research study.
Do not diagnose. Do not recommend treatment. Return only valid JSON.
Schema: {json.dumps(EXTRACTION_SCHEMA, ensure_ascii=False)}
Clinical note:
{note_text}
""".strip()


def parse_llm_json(raw_output: str) -> ExtractionResult:
    try:
        fields = json.loads(raw_output)
    except json.JSONDecodeError:
        fields = {key: "unknown" for key in EXTRACTION_SCHEMA}
    for key in EXTRACTION_SCHEMA:
        fields.setdefault(key, "unknown")
    safety = rule_based_red_flags(" ".join(str(v) for v in fields.values()))
    return ExtractionResult(fields=fields, requires_clinician_review=True, safety_flag=safety)
