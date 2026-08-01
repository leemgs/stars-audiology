"""Evaluation metrics for schema-constrained clinical-text extraction.

Implements the per-field evaluation prespecified in the manuscript (AI system
section), which goes beyond a single "field accuracy": exact match, precision /
recall / F1, omission rate, evidence-span agreement, and dedicated accuracy for
clinically load-bearing fields (temporal expressions, laterality, onset speed,
symptom duration). It also computes document-level exact match, run-to-run
consistency, and a clinically significant error rate (errors that could change a
referral decision).

The functions operate on already-extracted structured records so they can be
unit-tested without a language model. `confidence` in a predicted record is a
RULE-BASED reliability flag (span present/agreeing), not the model's token
probability -- see study_config.ai.confidence_flag.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Sequence

# Fields whose errors can change a referral decision (clinically significant).
REFERRAL_CRITICAL_FIELDS = {"laterality", "onset_speed", "sudden_loss", "vertigo",
                            "neurologic_sign"}


def _span_agree(pred: Optional[Sequence[int]], gold: Optional[Sequence[int]],
                tol: int = 0) -> bool:
    if pred is None or gold is None:
        return pred is None and gold is None
    return abs(pred[0] - gold[0]) <= tol and abs(pred[1] - gold[1]) <= tol


def field_metrics(gold_records: List[Dict[str, Any]],
                  pred_records: List[Dict[str, Any]],
                  fields: Sequence[str],
                  spans: Optional[Sequence[str]] = None) -> Dict[str, Dict[str, float]]:
    """Per-field exact match, precision/recall/F1, omission, span agreement.

    precision/recall/F1 are computed treating a non-null predicted value as a
    positive prediction and a non-null gold value as a condition positive; a
    field is correct when values match exactly.
    """
    assert len(gold_records) == len(pred_records)
    out: Dict[str, Dict[str, float]] = {}
    spans = set(spans or [])
    for f in fields:
        n = len(gold_records)
        exact = tp = fp = fn = omit = span_ok = span_total = 0
        for g, p in zip(gold_records, pred_records):
            gv, pv = g.get(f), p.get(f)
            if gv == pv:
                exact += 1
            if pv is not None and gv is not None and pv == gv:
                tp += 1
            elif pv is not None and pv != gv:
                fp += 1
            if gv is not None and pv is None:
                fn += 1
                omit += 1
            if f in spans:
                span_total += 1
                if _span_agree(p.get(f + "_span"), g.get(f + "_span")):
                    span_ok += 1
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec = tp / (tp + fn) if (tp + fn) else float("nan")
        f1 = (2 * prec * rec / (prec + rec)
              if prec == prec and rec == rec and (prec + rec) else float("nan"))
        rec_out = {
            "exact_match": exact / n if n else float("nan"),
            "precision": prec, "recall": rec, "f1": f1,
            "omission_rate": omit / n if n else float("nan"),
        }
        if f in spans:
            rec_out["span_agreement"] = span_ok / span_total if span_total else float("nan")
        out[f] = rec_out
    return out


def document_exact_match(gold_records, pred_records, fields) -> float:
    """Fraction of documents where ALL fields match exactly."""
    n = len(gold_records)
    if not n:
        return float("nan")
    ok = sum(all(g.get(f) == p.get(f) for f in fields)
             for g, p in zip(gold_records, pred_records))
    return ok / n


def clinically_significant_error_rate(gold_records, pred_records) -> float:
    """Fraction of documents with >=1 error in a referral-critical field."""
    n = len(gold_records)
    if not n:
        return float("nan")
    bad = 0
    for g, p in zip(gold_records, pred_records):
        if any(g.get(f) != p.get(f) for f in REFERRAL_CRITICAL_FIELDS
               if f in g or f in p):
            bad += 1
    return bad / n


def run_consistency(runs: List[List[Dict[str, Any]]], fields) -> float:
    """Mean fraction of fields identical across repeated generations (>=2 runs)."""
    if len(runs) < 2:
        return float("nan")
    n_docs = len(runs[0])
    agree = total = 0
    for i in range(n_docs):
        for f in fields:
            vals = {tuple_(runs[r][i].get(f)) for r in range(len(runs))}
            total += 1
            agree += 1 if len(vals) == 1 else 0
    return agree / total if total else float("nan")


def tuple_(v):
    return tuple(v) if isinstance(v, list) else v


if __name__ == "__main__":  # tiny self-check on toy data
    gold = [{"laterality": "left", "onset_speed": "acute", "duration_days": 3,
             "sudden_loss": True, "sudden_loss_span": [10, 21]}]
    pred = [{"laterality": "left", "onset_speed": "acute", "duration_days": 3,
             "sudden_loss": True, "sudden_loss_span": [10, 21]}]
    fields = ["laterality", "onset_speed", "duration_days", "sudden_loss"]
    m = field_metrics(gold, pred, fields, spans=["sudden_loss"])
    print("per-field:", m)
    print("doc exact match:", document_exact_match(gold, pred, fields))
    print("clinically significant error rate:",
          clinically_significant_error_rate(gold, pred))
    print("run consistency:", run_consistency([pred, pred], fields))
