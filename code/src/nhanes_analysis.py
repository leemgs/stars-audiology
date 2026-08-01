"""Real NHANES survey-weighted analysis for StressEar-AI.

This module runs the prespecified public-data analysis on **real** NHANES
public-use files. It is written against actual NHANES file names and variable
codes and performs design-based (survey-weighted, Taylor-linearized) estimation.

Data access
-----------
NHANES public-use ``.XPT`` files are published by the U.S. CDC at
``https://wwwn.cdc.gov/Nchs/Nhanes/<cycle>/<FILE>.XPT``. Two ways to supply them:

1. **Local files** (recommended / offline): download the files listed in
   ``REQUIRED_FILES`` and place them under ``code/data/raw/nhanes/<cycle>/``.
2. **Direct download**: pass ``--download`` to fetch them (requires outbound
   access to ``wwwn.cdc.gov``; some sandboxes block this by egress policy).

Then::

    python src/nhanes_analysis.py --cycles 2011-2012 2015-2016 2017-2018 \
        --data-dir data/raw/nhanes --out outputs/nhanes_results.json \
        --latex ../paper/tables/table_results.tex

The script writes a results JSON and a LaTeX results table ready to \\input into
the manuscript. It reports weighted prevalence with 95% CIs and design-based
logistic associations; it makes no causal claim.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

CDC_BASE = "https://wwwn.cdc.gov/Nchs/Nhanes"

# Per-cycle file stems. Audiometry exam (AUX), audiometry questionnaire (AUQ),
# demographics (DEMO), depression PHQ-9 (DPQ). Suffix letter differs by cycle.
CYCLE_SUFFIX = {
    "2011-2012": "G", "2013-2014": "H", "2015-2016": "I",
    "2017-2018": "J", "2017-2020": "P",  # P = pre-pandemic combined
}
REQUIRED_FILES = ["DEMO", "AUQ", "AUX", "DPQ"]

# Pure-tone threshold variables (air conduction, dB HL). NHANES names are stable
# across the covered cycles. R = right ear, L = left ear.
PTA_VARS = {
    "500":  ("AUXU500R", "AUXU500L"),
    "1000": ("AUXU1K1R", "AUXU1K1L"),
    "2000": ("AUXU2KR", "AUXU2KL"),
    "3000": ("AUXU3KR", "AUXU3KL"),
    "4000": ("AUXU4KR", "AUXU4KL"),
    "6000": ("AUXU6KR", "AUXU6KL"),
    "8000": ("AUXU8KR", "AUXU8KL"),
}
SPEECH_FREQS = ["500", "1000", "2000", "4000"]  # speech-frequency PTA

# Tinnitus: AUQ136 "bothered by ringing/roaring/buzzing in past 12 months"
# (1=Yes, 2=No). AUQ138 frequency (used for bothersome). Occupational noise:
# AUQ300 ever exposed to loud noise at work (>=3 months). PHQ-9: DPQ010..DPQ090.
DPQ_ITEMS = [f"DPQ0{i}0" for i in range(1, 10)]


@dataclass
class SurveyEstimate:
    estimate: float
    se: float
    n: int
    ci_low: float = field(init=False)
    ci_high: float = field(init=False)

    def __post_init__(self):
        self.ci_low = self.estimate - 1.96 * self.se
        self.ci_high = self.estimate + 1.96 * self.se


# --------------------------------------------------------------------------- #
# Design-based estimation (Taylor linearization, stratified, with-replacement)
# --------------------------------------------------------------------------- #
def svy_mean(y: np.ndarray, w: np.ndarray, strata: np.ndarray,
             psu: np.ndarray) -> SurveyEstimate:
    """Design-based weighted proportion/mean with Taylor-linearized SE.

    Implements the standard stratified, with-replacement PSU linearization used
    by survey packages: for the ratio estimator p = sum(w*y)/sum(w),
    var(p) = sum_h [ n_h/(n_h-1) * sum_i (u_hi - ubar_h)^2 ],
    with u_hi = sum_{j in PSU} w_ij (y_ij - p) / W.
    """
    y = np.asarray(y, float); w = np.asarray(w, float)
    m = np.isfinite(y) & np.isfinite(w) & (w > 0)
    y, w, strata, psu = y[m], w[m], np.asarray(strata)[m], np.asarray(psu)[m]
    W = w.sum()
    p = float((w * y).sum() / W)
    var = 0.0
    for h in np.unique(strata):
        hs = strata == h
        psu_h = psu[hs]
        ups = np.unique(psu_h)
        n_h = len(ups)
        if n_h < 2:
            continue  # single-PSU stratum contributes 0 (conservative)
        u = np.array([(w[hs][psu_h == a] *
                       (y[hs][psu_h == a] - p)).sum() / W for a in ups])
        ubar = u.mean()
        var += (n_h / (n_h - 1.0)) * ((u - ubar) ** 2).sum()
    return SurveyEstimate(estimate=p, se=float(np.sqrt(max(var, 0.0))), n=int(m.sum()))


def svy_logistic(df: pd.DataFrame, outcome: str, predictors: List[str],
                 weight: str, strata: str, psu: str) -> Optional[dict]:
    """Design-weighted logistic regression with a design-based (linearized) SE.

    Point estimates: pseudo-maximum-likelihood weighted logistic (weights scaled
    to sum to the sample size). Standard errors: a manually computed
    cluster-robust sandwich with stratum finite-population correction --- the
    textbook Taylor linearization for stratified multistage survey logistic
    models --- so we do not rely on statsmodels' unsupported weighted cluster
    covariance. Returns odds ratios with 95% CIs.
    """
    try:
        import statsmodels.api as sm
    except Exception:
        return None
    cols = [outcome] + predictors + [weight, strata, psu]
    d = df[cols].dropna().copy()
    if d[outcome].nunique() < 2 or len(d) < 50:
        return None
    y = d[outcome].astype(int).values.astype(float)
    Xdf = sm.add_constant(d[predictors].astype(float))
    X = Xdf.values.astype(float)
    w = d[weight].astype(float).values
    w = w * (len(w) / w.sum())          # scale to sum to n (relative weights)

    # Point estimates via weighted IRLS.
    res = sm.GLM(y, X, family=sm.families.Binomial(),
                 var_weights=w).fit()
    beta = res.params
    p = 1.0 / (1.0 + np.exp(-(X @ beta)))

    # Bread: inverse weighted information matrix.
    Wd = w * p * (1.0 - p)
    bread = np.linalg.pinv((X * Wd[:, None]).T @ X)

    # Meat: cluster-summed weighted scores with stratum correction.
    score = (w * (y - p))[:, None] * X                     # per-obs score
    strat = d[strata].astype(str).values
    clus = (strat + "_" + d[psu].astype(str).values)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for h in np.unique(strat):
        hs = strat == h
        cl_h = clus[hs]
        ups = np.unique(cl_h)
        n_h = len(ups)
        if n_h < 2:
            continue
        u = np.array([score[hs][cl_h == a].sum(axis=0) for a in ups])
        ubar = u.mean(axis=0)
        centered = u - ubar
        meat += (n_h / (n_h - 1.0)) * (centered.T @ centered)
    cov = bread @ meat @ bread
    se = np.sqrt(np.clip(np.diag(cov), 0, None))

    names = list(Xdf.columns)
    out = {}
    for name in predictors:
        j = names.index(name)
        b, s = beta[j], se[j]
        z = b / s if s > 0 else np.nan
        from math import erf, sqrt
        pval = 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2)))) if s > 0 else np.nan
        out[name] = {
            "odds_ratio": float(np.exp(b)),
            "ci_low": float(np.exp(b - 1.96 * s)),
            "ci_high": float(np.exp(b + 1.96 * s)),
            "p_value": float(pval),
        }
    out["_n"] = int(len(d))
    return out


# --------------------------------------------------------------------------- #
# Loading and variable derivation
# --------------------------------------------------------------------------- #
def _read_xpt(path: Path) -> pd.DataFrame:
    """Read a SAS XPORT file, validating the magic header first.

    A common failure is a saved HTML page (e.g., a server block page) rather than
    the binary XPORT file; valid XPORT files begin with 'HEADER RECORD'.
    """
    with open(path, "rb") as fh:
        magic = fh.read(80)
    if not magic.lstrip().startswith(b"HEADER RECORD"):
        head = magic[:120].decode("latin-1", "replace")
        raise ValueError(
            f"{path} is not a valid XPORT file (starts with {head!r}). It is most "
            f"likely an HTML page saved during download. Re-download with a browser "
            f"User-Agent (this script now does), or fetch the file manually.")
    try:
        return pd.read_sas(path, format="xport")
    except Exception:
        import pyreadstat  # more tolerant fallback
        df, _ = pyreadstat.read_xport(str(path))
        return df


def _cycle_path(data_dir: Path, cycle: str, stem: str) -> Path:
    suf = CYCLE_SUFFIX[cycle]
    return data_dir / cycle / f"{stem}_{suf}.XPT"


_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 StressEar-AI-research")


def _http_download(url: str, dest: Path) -> None:
    """Download `url` to `dest`, sending a browser User-Agent and validating that
    the payload is a real XPORT file (CDC returns an HTML page to the default
    Python-urllib agent)."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = resp.read()
    if not data.lstrip()[:20].startswith(b"HEADER RECORD"):
        ctype = ""
        try:
            ctype = resp.headers.get("Content-Type", "")
        except Exception:
            pass
        snippet = data[:160].decode("latin-1", "replace")
        raise ValueError(
            f"Server did not return an XPORT file for {url} "
            f"(Content-Type={ctype!r}; first bytes={snippet!r}). "
            f"If this persists, download the file in a browser and place it at {dest}.")
    dest.write_bytes(data)


def _is_valid_xpt(path: Path) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(80).lstrip().startswith(b"HEADER RECORD")
    except Exception:
        return False


def download_cycle(cycle: str, data_dir: Path) -> None:
    suf = CYCLE_SUFFIX[cycle]
    (data_dir / cycle).mkdir(parents=True, exist_ok=True)
    for stem in REQUIRED_FILES:
        url = f"{CDC_BASE}/{cycle}/{stem}_{suf}.XPT"
        dest = _cycle_path(data_dir, cycle, stem)
        # Re-download if missing, empty, or a previously-saved HTML/bad file.
        if dest.exists() and dest.stat().st_size > 0 and _is_valid_xpt(dest):
            continue
        print(f"  downloading {url}")
        _http_download(url, dest)


def load_cycle(cycle: str, data_dir: Path) -> pd.DataFrame:
    frames = {}
    for stem in REQUIRED_FILES:
        p = _cycle_path(data_dir, cycle, stem)
        if not p.exists():
            raise FileNotFoundError(
                f"Missing {p}. Download {stem}_{CYCLE_SUFFIX[cycle]}.XPT from "
                f"{CDC_BASE}/{cycle}/ or pass --download.")
        frames[stem] = _read_xpt(p)
    df = frames["DEMO"]
    for stem in ["AUQ", "AUX", "DPQ"]:
        df = df.merge(frames[stem], on="SEQN", how="left")
    df["cycle"] = cycle
    return df


def derive_variables(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["cycle"] = df["cycle"]
    out["age"] = df["RIDAGEYR"]
    out["sex"] = (df["RIAGENDR"] == 2).astype(float)          # 1=female
    out["weight"] = df.get("WTMEC2YR")
    out["strata"] = df.get("SDMVSTRA")
    out["psu"] = df.get("SDMVPSU")
    # Tinnitus (AUQ136: 1=yes, 2=no)
    if "AUQ136" in df:
        out["tinnitus"] = df["AUQ136"].map({1: 1, 2: 0})
    # Occupational loud-noise exposure (AUQ300: 1=yes)
    if "AUQ300" in df:
        out["occ_noise"] = df["AUQ300"].map({1: 1, 2: 0})
    # PHQ-9 depression score (items 0-3; >=10 = screen positive)
    items = [c for c in DPQ_ITEMS if c in df]
    if items:
        phq = df[items].replace({7: np.nan, 9: np.nan}).sum(axis=1, min_count=len(items))
        out["phq9"] = phq
        out["depressed"] = (phq >= 10).astype(float)
    # Better/worse ear speech-frequency PTA
    r = [PTA_VARS[f][0] for f in SPEECH_FREQS if PTA_VARS[f][0] in df]
    l = [PTA_VARS[f][1] for f in SPEECH_FREQS if PTA_VARS[f][1] in df]
    if len(r) == len(SPEECH_FREQS) and len(l) == len(SPEECH_FREQS):
        rr = df[r].replace({888: np.nan, 666: np.nan}).mean(axis=1)
        ll = df[l].replace({888: np.nan, 666: np.nan}).mean(axis=1)
        out["better_ear_pta"] = np.minimum(rr, ll)
        out["worse_ear_pta"] = np.maximum(rr, ll)
        out["hearing_loss"] = (out["better_ear_pta"] > 25).astype(float)
    out["age_band"] = pd.cut(out["age"], [39, 49, 59, 69], labels=["40-49", "50-59", "60-69"])
    return out


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #
def run_analysis(df: pd.DataFrame, age_min=40, age_max=69) -> dict:
    d = df[(df["age"] >= age_min) & (df["age"] <= age_max)].copy()
    res: Dict[str, object] = {"n_analytic": int(len(d)), "age_range": [age_min, age_max]}

    def prev(col):
        if col not in d:
            return None
        e = svy_mean(d[col].values, d["weight"].values, d["strata"].values, d["psu"].values)
        return {"prevalence": e.estimate, "se": e.se,
                "ci": [e.ci_low, e.ci_high], "n": e.n}

    res["prevalence"] = {k: prev(k) for k in ["tinnitus", "hearing_loss", "depressed"]}

    # Associations (design-based logistic ORs), minimal adjustment set.
    if {"tinnitus", "age", "sex"}.issubset(d.columns):
        preds = [p for p in ["occ_noise", "depressed", "age", "sex"] if p in d]
        res["assoc_tinnitus"] = svy_logistic(d, "tinnitus", preds,
                                              "weight", "strata", "psu")
    if {"hearing_loss", "age", "sex"}.issubset(d.columns):
        preds = [p for p in ["occ_noise", "depressed", "age", "sex"] if p in d]
        res["assoc_hearing_loss"] = svy_logistic(d, "hearing_loss", preds,
                                                  "weight", "strata", "psu")
    return res


def to_latex(res: dict) -> str:
    def fmt_prev(x):
        return ("--" if not x else
                f"{100*x['prevalence']:.1f}\\% ({100*x['ci'][0]:.1f}--{100*x['ci'][1]:.1f})")
    lines = [
        "\\begin{table}[htbp]", "\\centering",
        "\\caption{Real NHANES survey-weighted results (adults 40--69). "
        "Estimates are design-based (Taylor-linearized); associations are "
        "odds ratios from design-weighted logistic regression and are not "
        "causal. Generated by \\texttt{code/src/nhanes\\_analysis.py}.}",
        "\\label{tab:results}", "\\small", "\\begin{tabular}{lll}", "\\toprule",
        "Quantity & Estimate (95\\% CI) & $N$ \\\\", "\\midrule",
    ]
    for key, lab in [("tinnitus", "Tinnitus prevalence"),
                     ("hearing_loss", "Hearing loss ($>$25 dB HL) prevalence"),
                     ("depressed", "Depression (PHQ-9$\\geq$10) prevalence")]:
        x = res.get("prevalence", {}).get(key)
        n = x["n"] if x else "--"
        lines.append(f"{lab} & {fmt_prev(x)} & {n} \\\\")
    for akey, lab in [("assoc_tinnitus", "Tinnitus"),
                      ("assoc_hearing_loss", "Hearing loss")]:
        a = res.get(akey)
        if a and "depressed" in a:
            o = a["depressed"]
            lines.append(f"{lab}: OR depressed mood & "
                         f"{o['odds_ratio']:.2f} ({o['ci_low']:.2f}--{o['ci_high']:.2f}) & "
                         f"{a['_n']} \\\\")
        if a and "occ_noise" in a:
            o = a["occ_noise"]
            lines.append(f"{lab}: OR occupational noise & "
                         f"{o['odds_ratio']:.2f} ({o['ci_low']:.2f}--{o['ci_high']:.2f}) & "
                         f"{a['_n']} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", nargs="+", default=["2011-2012", "2015-2016", "2017-2018"])
    ap.add_argument("--data-dir", default="data/raw/nhanes")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--out", default="outputs/nhanes_results.json")
    ap.add_argument("--latex", default=None)
    args = ap.parse_args()
    data_dir = Path(args.data_dir)

    frames = []
    for cyc in args.cycles:
        if args.download:
            download_cycle(cyc, data_dir)
        frames.append(derive_variables(load_cycle(cyc, data_dir)))
    df = pd.concat(frames, ignore_index=True)

    # Diagnostic: report which derived variables were populated (helps catch
    # cycle-specific variable-name differences instead of silently missing them).
    print("Derived-variable coverage (non-null counts):")
    for v in ["tinnitus", "hearing_loss", "better_ear_pta", "worse_ear_pta",
              "depressed", "occ_noise", "age", "sex", "weight"]:
        n = int(df[v].notna().sum()) if v in df else 0
        flag = "" if (v in df and n > 0) else "   <-- MISSING/empty (check variable codes)"
        print(f"  {v:16s}: {n}{flag}")

    res = run_analysis(df)
    res["cycles"] = args.cycles
    res["n_total_rows"] = int(len(df))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    if args.latex:
        Path(args.latex).write_text(to_latex(res), encoding="utf-8")
        print(f"Wrote {args.latex}")
    print(json.dumps(res.get("prevalence", {}), indent=2))


if __name__ == "__main__":
    main()
