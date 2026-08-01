"""Correctness tests for the NHANES design-based estimators.

These validate the *statistics* (not the CDC download) so the pipeline can be
trusted the moment real .XPT files are supplied. Run:

    python src/test_nhanes_analysis.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nhanes_analysis import svy_mean, svy_logistic, derive_variables, run_analysis


def test_svy_mean_point_estimate_matches_hajek():
    rng = np.random.default_rng(0)
    n = 2000
    y = rng.binomial(1, 0.3, n).astype(float)
    w = rng.uniform(1, 5, n)
    strata = rng.integers(0, 10, n)
    psu = rng.integers(0, 2, n)
    est = svy_mean(y, w, strata, psu)
    hajek = (w * y).sum() / w.sum()
    assert abs(est.estimate - hajek) < 1e-9, "weighted proportion wrong"
    assert est.se > 0 and np.isfinite(est.se), "SE must be finite/positive"
    assert est.ci_low < est.estimate < est.ci_high


def test_svy_mean_zero_variance_when_constant():
    y = np.ones(100)
    w = np.ones(100)
    strata = np.repeat([0, 1], 50)
    psu = np.tile([0, 1], 50)
    est = svy_mean(y, w, strata, psu)
    assert est.estimate == 1.0 and est.se == 0.0


def test_svy_logistic_recovers_planted_effect():
    rng = np.random.default_rng(42)
    n = 4000
    x = rng.binomial(1, 0.5, n)
    # true log-odds: intercept -1.0, effect of x = ln(2)
    logit = -1.0 + np.log(2.0) * x
    y = rng.binomial(1, 1 / (1 + np.exp(-logit)))
    df = pd.DataFrame({
        "y": y, "x": x, "age": rng.integers(40, 70, n),
        "weight": rng.uniform(1, 3, n),
        "strata": rng.integers(0, 8, n), "psu": rng.integers(0, 2, n),
    })
    out = svy_logistic(df, "y", ["x", "age"], "weight", "strata", "psu")
    assert out is not None
    or_x = out["x"]["odds_ratio"]
    assert 1.5 < or_x < 2.6, f"planted OR~2 not recovered: {or_x:.2f}"
    assert out["x"]["ci_low"] < or_x < out["x"]["ci_high"]


def test_derive_and_run_on_synthetic_nhanes_frame():
    """Build an NHANES-shaped frame (real column names) and run end-to-end."""
    rng = np.random.default_rng(7)
    n = 1500
    raw = pd.DataFrame({
        "SEQN": np.arange(n),
        "RIDAGEYR": rng.integers(40, 70, n),
        "RIAGENDR": rng.choice([1, 2], n),
        "WTMEC2YR": rng.uniform(5000, 40000, n),
        "SDMVSTRA": rng.integers(100, 115, n),
        "SDMVPSU": rng.choice([1, 2], n),
        "AUQ136": rng.choice([1, 2], n, p=[0.2, 0.8]),
        "AUQ300": rng.choice([1, 2], n, p=[0.3, 0.7]),
        "cycle": "2017-2018",
    })
    for i in range(1, 10):
        raw[f"DPQ0{i}0"] = rng.integers(0, 4, n)
    for f, (rv, lv) in {
        "500": ("AUXU500R", "AUXU500L"), "1000": ("AUXU1K1R", "AUXU1K1L"),
        "2000": ("AUXU2KR", "AUXU2KL"), "4000": ("AUXU4KR", "AUXU4KL"),
    }.items():
        raw[rv] = rng.normal(20, 12, n)
        raw[lv] = rng.normal(20, 12, n)
    d = derive_variables(raw)
    res = run_analysis(d)
    assert res["prevalence"]["tinnitus"]["prevalence"] > 0
    assert res["prevalence"]["hearing_loss"] is not None
    assert 0 <= res["prevalence"]["tinnitus"]["ci"][0] <= 1


def _run_all():
    for fn in [test_svy_mean_point_estimate_matches_hajek,
               test_svy_mean_zero_variance_when_constant,
               test_svy_logistic_recovers_planted_effect,
               test_derive_and_run_on_synthetic_nhanes_frame]:
        fn()
        print(f"  [PASS] {fn.__name__}")
    print("All NHANES estimator tests passed. Supply real .XPT files to get real "
          "results:  python src/nhanes_analysis.py --data-dir data/raw/nhanes "
          "--cycles 2011-2012 2015-2016 2017-2018 --latex ../paper/tables/table_results.tex")


if __name__ == "__main__":
    _run_all()
