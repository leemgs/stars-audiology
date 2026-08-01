"""Correctness tests for the KNHANES loader/derivation and analysis.

Validates the mapping-driven derivation and that the perceived-stress exposure
flows into the association models, using a synthetic KNHANES-shaped frame (real
KNHANES data require KDCA approval). Run:  python src/test_knhanes_analysis.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import knhanes_analysis as K

TEST_MAPPING = {
    "survey_design": {"weight": "wt_tot", "strata": "kstrata", "psu": "psu"},
    "common": {"age": "age", "sex": "sex", "education": "edu",
               "income": "ho_incm", "occupation": "occp", "employment": "EC_stt_1"},
    "exposure": {"perceived_stress": "BP1", "stress_high_values": [1, 2]},
    "mediators": {"depression_phq9_items": [], "depressed_2wk": "BP5",
                  "sleep_hours": "slp"},
    "outcomes": {"tinnitus_item": "tin_q", "tinnitus_yes_values": [1],
                 "occupational_noise": "noise_q"},
    "audiometry": {
        "500": ["O_R_500", "O_L_500"], "1000": ["O_R_1000", "O_L_1000"],
        "2000": ["O_R_2000", "O_L_2000"], "4000": ["O_R_4000", "O_L_4000"],
        "invalid_threshold_codes": [999, 666]},
    "speech_freqs": ["500", "1000", "2000", "4000"],
    "analysis": {"age_min": 40, "age_max": 69, "hearing_loss_cutoff_db": 25},
}


def _synthetic(n=1500, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "age": rng.integers(40, 70, n), "sex": rng.choice([1, 2], n),
        "BP1": rng.choice([1, 2, 3, 4], n), "BP5": rng.choice([1, 2], n),
        "tin_q": rng.choice([1, 2], n, p=[0.25, 0.75]),
        "noise_q": rng.choice([1, 2], n, p=[0.3, 0.7]),
        "wt_tot": rng.uniform(1000, 9000, n),
        "kstrata": rng.integers(1, 12, n), "psu": rng.choice([1, 2], n),
        "slp": rng.uniform(4, 9, n), "cycle": "2011",
    })
    for f in ["O_R_500", "O_L_500", "O_R_1000", "O_L_1000",
              "O_R_2000", "O_L_2000", "O_R_4000", "O_L_4000"]:
        col = rng.normal(20, 12, n).astype(float)
        col[rng.random(n) < 0.2] = np.nan   # some without audiometry
        df[f] = col
    return df


def test_derivation():
    d = K.derive_variables(_synthetic(), TEST_MAPPING)
    # perceived stress dichotomized (BP1 in {1,2} -> 1)
    assert set(pd.unique(d["perceived_stress"].dropna())) <= {0.0, 1.0}
    # hearing_loss must be NaN where audiometry missing (not counted as 0)
    assert d["hearing_loss"].isna().sum() > 0
    assert d["tinnitus"].notna().all()
    assert {"better_ear_pta", "worse_ear_pta"}.issubset(d.columns)


def test_analysis_uses_perceived_stress():
    d = K.derive_variables(_synthetic(), TEST_MAPPING)
    res = K.run_analysis(d, TEST_MAPPING)
    assert res["prevalence"]["perceived_stress"]["prevalence"] > 0
    at = res.get("assoc_tinnitus")
    # If statsmodels is available the primary exposure must be modeled.
    if at is not None:
        assert "perceived_stress" in at


def test_latex_renders():
    d = K.derive_variables(_synthetic(), TEST_MAPPING)
    tex = K.to_latex(K.run_analysis(d, TEST_MAPPING))
    assert "Perceived stress" in tex and "tab:results_knhanes" in tex


def _run_all():
    import warnings; warnings.filterwarnings("ignore")
    for fn in [test_derivation, test_analysis_uses_perceived_stress, test_latex_renders]:
        fn(); print(f"  [PASS] {fn.__name__}")
    print("KNHANES loader tests passed. Supply KDCA-approved files + a "
          "codebook-verified mapping to produce the primary perceived-stress results.")


if __name__ == "__main__":
    _run_all()
