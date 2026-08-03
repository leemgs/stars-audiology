"""Real NHANES survey-weighted analysis for STARS.

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
def _linearized_var(u: np.ndarray, strata: np.ndarray, psu: np.ndarray,
                    single_psu: str = "center") -> np.ndarray:
    """Stratified, with-replacement variance of a linearized total from
    per-observation influence values ``u`` (scalars or K-vectors per row).

    Aggregates ``u`` to PSU totals within strata and sums the standard
    ``n_h/(n_h-1) * Sigma (t_ha - tbar_h)^2`` contribution. **Single-PSU (lonely)
    strata** are handled by ``single_psu``:

    - ``"center"`` (default): center the lone PSU total at the grand mean of all
      PSU totals and add ``(t - tbar_grand)^2`` --- the standard *conservative*
      option (equivalent to R ``survey``'s ``options(survey.lonely.psu="adjust")``).
      Dropping the term instead (the old behavior) *under*-estimates variance.
    - ``"certainty"``: treat the stratum as a self-representing certainty PSU
      contributing 0 variance (only correct when it truly is a certainty unit).
    - ``"drop"``: legacy behavior (contributes 0); retained for comparison.

    ``u`` may be 1-D (scalar influence, e.g. svy_mean) or 2-D ``(n, K)``
    (vector influence, e.g. the score contributions of svy_logistic); the return
    is a scalar variance or a ``(K, K)`` matrix accordingly.
    """
    u = np.asarray(u, float)
    vec = u.ndim == 2
    K = u.shape[1] if vec else 1
    strata = np.asarray(strata); psu = np.asarray(psu)

    # PSU totals grouped by stratum, plus every PSU total for the grand mean.
    per_stratum = []            # list of (n_h, totals array)
    all_totals = []
    for h in np.unique(strata):
        hs = strata == h
        ph = psu[hs]; uh = u[hs]
        ups = np.unique(ph)
        tot = np.array([uh[ph == a].sum(axis=0) for a in ups])  # (n_h,) or (n_h,K)
        per_stratum.append((len(ups), tot))
        all_totals.append(tot)
    all_totals = np.concatenate(all_totals, axis=0) if all_totals else np.zeros(
        (0, K) if vec else 0)
    grand = all_totals.mean(axis=0) if len(all_totals) else (
        np.zeros(K) if vec else 0.0)

    var = np.zeros((K, K)) if vec else 0.0
    for n_h, tot in per_stratum:
        if n_h >= 2:
            tbar = tot.mean(axis=0)
            c = tot - tbar
            var = var + (n_h / (n_h - 1.0)) * (c.T @ c if vec else float((c ** 2).sum()))
        elif single_psu == "center":
            c = tot[0] - grand           # lone PSU centered at the grand mean
            var = var + (np.outer(c, c) if vec else float(c * c))
        # "certainty"/"drop": contribute 0
    return var


def svy_mean(y: np.ndarray, w: np.ndarray, strata: np.ndarray,
             psu: np.ndarray, domain: Optional[np.ndarray] = None,
             single_psu: str = "center") -> SurveyEstimate:
    """Design-based weighted proportion/mean with Taylor-linearized SE.

    Implements the standard stratified, with-replacement PSU linearization for
    the ratio estimator ``p = sum(w*y)/sum(w)``.

    **Domain (subpopulation) estimation.** Pass ``domain`` (a boolean array over
    all rows) to estimate within a subpopulation *without subsetting the design*:
    all rows with a valid weight are retained for the stratum/PSU variance
    structure, and out-of-domain (or missing-outcome) rows contribute a zero
    influence rather than being deleted. This is the correct way to estimate,
    e.g., the 40--69 age band, and avoids the SE distortion that naive
    pre-subsetting introduces. With ``domain=None`` every observed row is in the
    domain (back-compatible).

    **Single-PSU strata** are handled by ``single_psu`` (see ``_linearized_var``);
    the default ``"center"`` is conservative, unlike the old silent drop.
    """
    y = np.asarray(y, float); w = np.asarray(w, float)
    valid = np.isfinite(w) & (w > 0)                 # keep all design members
    if domain is None:
        dom = np.isfinite(y)
    else:
        dom = np.asarray(domain, bool) & np.isfinite(y)
    strata = np.asarray(strata); psu = np.asarray(psu)
    y, w, strata, psu, dom = (a[valid] for a in (y, w, strata, psu, dom))
    ind = dom.astype(float)
    y_safe = np.where(np.isfinite(y), y, 0.0)        # y only used where ind=1
    Xhat = float((w * ind).sum())
    if Xhat <= 0:
        return SurveyEstimate(estimate=float("nan"), se=float("nan"), n=0)
    p = float((w * ind * y_safe).sum() / Xhat)
    u = ind * w * (y_safe - p) / Xhat                # influence; 0 outside domain
    var = _linearized_var(u, strata, psu, single_psu)
    return SurveyEstimate(estimate=p, se=float(np.sqrt(max(float(var), 0.0))),
                          n=int(ind.sum()))


def svy_logistic(df: pd.DataFrame, outcome: str, predictors: List[str],
                 weight: str, strata: str, psu: str,
                 domain=None, single_psu: str = "center") -> Optional[dict]:
    """Design-weighted logistic regression with a design-based (linearized) SE.

    Point estimates: pseudo-maximum-likelihood weighted logistic (weights scaled
    to sum to the sample size). Standard errors: a cluster-robust sandwich with
    stratum correction --- the textbook Taylor linearization for stratified
    multistage survey logistic models --- so we do not rely on statsmodels'
    unsupported weighted cluster covariance. Returns odds ratios with 95% CIs.

    **Domain (subpopulation) estimation.** ``domain`` (a boolean array/Series
    over ``df`` rows, or a column name) restricts the *fitted* observations while
    the sandwich ``meat`` is accumulated over the *full design* (every row with
    valid design variables): out-of-domain and item-missing rows contribute a
    zero score but still define the stratum/PSU structure. This avoids the SE
    distortion of pre-subsetting the data before variance estimation.

    **Single-PSU strata** use the conservative centering option by default
    (``single_psu``; see ``_linearized_var``) instead of being silently dropped.
    """
    try:
        import statsmodels.api as sm
    except Exception:
        return None
    design_cols = [weight, strata, psu]
    if isinstance(domain, str):
        dmask = df[domain].astype(bool).to_numpy()
    elif domain is None:
        dmask = np.ones(len(df), bool)
    else:
        dmask = np.asarray(domain, bool)

    dv = df[design_cols].notna().all(axis=1).to_numpy() & (
        df[weight].to_numpy() > 0)                              # design-valid rows
    complete = df[[outcome] + predictors].notna().all(axis=1).to_numpy()
    fit_mask = dv & dmask & complete                           # rows entering the fit
    if int(fit_mask.sum()) < 50 or df.loc[fit_mask, outcome].nunique() < 2:
        return None

    dfit = df.loc[fit_mask]
    y = dfit[outcome].astype(float).to_numpy()
    Xdf = sm.add_constant(dfit[predictors].astype(float))
    X = Xdf.to_numpy(dtype=float)
    w = dfit[weight].astype(float).to_numpy()
    w = w * (len(w) / w.sum())          # scale to sum to n (relative weights)

    # Point estimates via weighted IRLS.
    res = sm.GLM(y, X, family=sm.families.Binomial(), var_weights=w).fit()
    beta = res.params
    p = 1.0 / (1.0 + np.exp(-(X @ beta)))

    # Bread: inverse weighted information matrix (fitted rows).
    Wd = w * p * (1.0 - p)
    bread = np.linalg.pinv((X * Wd[:, None]).T @ X)

    # Meat: per-observation scores placed on the FULL design (0 outside the fit),
    # then the stratified/clustered linearized variance with lonely-PSU centering.
    K = X.shape[1]
    dv_pos = {ix: i for i, ix in enumerate(df.index[dv])}
    score_all = np.zeros((int(dv.sum()), K))
    score_fit = (w * (y - p))[:, None] * X
    for j, ix in enumerate(dfit.index):
        score_all[dv_pos[ix]] = score_fit[j]
    strat_dv = df.loc[dv, strata].astype(str).to_numpy()
    psu_dv = df.loc[dv, psu].astype(str).to_numpy()
    meat = _linearized_var(score_all, strat_dv, psu_dv, single_psu)
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
    out["_n"] = int(len(dfit))
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
        try:
            import pyreadstat  # more tolerant fallback (optional)
        except Exception:
            raise
        df, _ = pyreadstat.read_xport(str(path))
        return df


def _cycle_path(data_dir: Path, cycle: str, stem: str) -> Path:
    suf = CYCLE_SUFFIX[cycle]
    return data_dir / cycle / f"{stem}_{suf}.XPT"


_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 STARS-research")


def _candidate_urls(cycle: str, stem: str) -> List[str]:
    """Candidate CDC URLs for a NHANES file, newest layout first.

    The 2024 CDC site migration moved public NHANES files from
    ``/Nchs/Nhanes/<cycle>/<FILE>.XPT`` (now 404) to
    ``/Nchs/Data/Nhanes/Public/<beginYear>/DataFiles/<FILE>.xpt``. We try the new
    layout first, then the legacy one, and both cases of the extension.
    """
    suf = CYCLE_SUFFIX[cycle]
    f = f"{stem}_{suf}"
    begin = cycle.split("-")[0]
    new = f"https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{begin}/DataFiles"
    return [
        f"{new}/{f}.xpt", f"{new}/{f}.XPT",
        f"{CDC_BASE}/{cycle}/{f}.XPT", f"{CDC_BASE}/{cycle}/{f}.xpt",
    ]


def _try_fetch(url: str) -> Optional[bytes]:
    """Return XPORT bytes if `url` serves a real XPORT file, else None."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = resp.read()
    except Exception:
        return None
    return data if data.lstrip()[:20].startswith(b"HEADER RECORD") else None


def _is_valid_xpt(path: Path) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(80).lstrip().startswith(b"HEADER RECORD")
    except Exception:
        return False


def download_cycle(cycle: str, data_dir: Path) -> None:
    (data_dir / cycle).mkdir(parents=True, exist_ok=True)
    for stem in REQUIRED_FILES:
        dest = _cycle_path(data_dir, cycle, stem)
        # Re-download if missing, empty, or a previously-saved HTML/bad file.
        if dest.exists() and dest.stat().st_size > 0 and _is_valid_xpt(dest):
            continue
        data, tried = None, []
        for url in _candidate_urls(cycle, stem):
            tried.append(url)
            print(f"  trying {url}")
            data = _try_fetch(url)
            if data is not None:
                print("    -> OK (valid XPORT)")
                break
        if data is None:
            raise ValueError(
                "None of the candidate CDC URLs returned a valid XPORT file for "
                f"{stem}_{CYCLE_SUFFIX[cycle]} ({cycle}). Tried:\n  " +
                "\n  ".join(tried) +
                f"\nDownload it in a browser from the NHANES data page and place it "
                f"at {dest}, then re-run without --download.")
        dest.write_bytes(data)


def load_cycle(cycle: str, data_dir: Path) -> pd.DataFrame:
    frames = {}
    for stem in REQUIRED_FILES:
        p = _cycle_path(data_dir, cycle, stem)
        if not p.exists():
            begin = cycle.split("-")[0]
            raise FileNotFoundError(
                f"Missing {p}. Pass --download, or fetch {stem}_{CYCLE_SUFFIX[cycle]}.xpt "
                f"from https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/{begin}/DataFiles/ "
                f"and place it there.")
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
    # PHQ-9 depression score (items 0-3; >=10 = screen positive). Preserve NaN:
    # participants without a complete PHQ-9 must be MISSING, not counted as 0.
    items = [c for c in DPQ_ITEMS if c in df]
    if items:
        phq = df[items].replace({7: np.nan, 9: np.nan}).sum(axis=1, min_count=len(items))
        out["phq9"] = phq
        out["depressed"] = np.where(phq.notna(), (phq >= 10).astype(float), np.nan)
    # Better/worse ear speech-frequency PTA
    r = [PTA_VARS[f][0] for f in SPEECH_FREQS if PTA_VARS[f][0] in df]
    l = [PTA_VARS[f][1] for f in SPEECH_FREQS if PTA_VARS[f][1] in df]
    if len(r) == len(SPEECH_FREQS) and len(l) == len(SPEECH_FREQS):
        rr = df[r].replace({888: np.nan, 666: np.nan}).mean(axis=1)
        ll = df[l].replace({888: np.nan, 666: np.nan}).mean(axis=1)
        out["better_ear_pta"] = np.minimum(rr, ll)
        out["worse_ear_pta"] = np.maximum(rr, ll)
        # Preserve NaN: participants without audiometry are MISSING, not "no loss".
        out["hearing_loss"] = np.where(
            out["better_ear_pta"].notna(),
            (out["better_ear_pta"] > 25).astype(float), np.nan)
    out["age_band"] = pd.cut(out["age"], [39, 49, 59, 69], labels=["40-49", "50-59", "60-69"])
    return out


# --------------------------------------------------------------------------- #
# Analysis
# --------------------------------------------------------------------------- #
def run_analysis(df: pd.DataFrame, age_min=40, age_max=69) -> dict:
    # Domain (subpopulation) estimation: keep the FULL design and mark the 40--69
    # analytic band as the domain, rather than subsetting before variance
    # estimation (which distorts the stratum/PSU structure and the SEs).
    dom = ((df["age"] >= age_min) & (df["age"] <= age_max)).to_numpy()
    res: Dict[str, object] = {"n_analytic": int(dom.sum()),
                              "age_range": [age_min, age_max]}

    def prev(col):
        if col not in df:
            return None
        e = svy_mean(df[col].to_numpy(), df["weight"].to_numpy(),
                     df["strata"].to_numpy(), df["psu"].to_numpy(), domain=dom)
        return {"prevalence": e.estimate, "se": e.se,
                "ci": [e.ci_low, e.ci_high], "n": e.n}

    res["prevalence"] = {k: prev(k) for k in ["tinnitus", "hearing_loss", "depressed"]}

    # Associations (design-based logistic ORs), minimal adjustment set, estimated
    # on the 40--69 domain over the full design.
    if {"tinnitus", "age", "sex"}.issubset(df.columns):
        preds = [p for p in ["occ_noise", "depressed", "age", "sex"] if p in df]
        res["assoc_tinnitus"] = svy_logistic(df, "tinnitus", preds,
                                              "weight", "strata", "psu", domain=dom)
    if {"hearing_loss", "age", "sex"}.issubset(df.columns):
        preds = [p for p in ["occ_noise", "depressed", "age", "sex"] if p in df]
        res["assoc_hearing_loss"] = svy_logistic(df, "hearing_loss", preds,
                                                  "weight", "strata", "psu", domain=dom)
    return res


def to_latex(res: dict) -> str:
    def fmt_prev(x):
        return ("--" if not x else
                f"{100*x['prevalence']:.1f}\\% ({100*x['ci'][0]:.1f}--{100*x['ci'][1]:.1f})")

    def stars(p):
        if p is None:
            return ""
        return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""

    def cell(a, key):
        if not a or key not in a:
            return "--"
        o = a[key]
        return (f"{o['odds_ratio']:.2f} ({o['ci_low']:.2f}--{o['ci_high']:.2f})"
                f"{stars(o.get('p_value'))}")

    at = res.get("assoc_tinnitus")
    ah = res.get("assoc_hearing_loss")
    pv = res.get("prevalence", {})
    nt = at["_n"] if at else (pv.get("tinnitus", {}) or {}).get("n", "--")
    nh = ah["_n"] if ah else (pv.get("hearing_loss", {}) or {}).get("n", "--")
    lines = [
        "\\begin{table}[htbp]", "\\centering",
        "\\caption{\\textbf{Real NHANES results} (U.S. adults 40--69; pooled "
        "2011--2012, 2015--2016, 2017--2018). Prevalence is design-based "
        "(survey-weighted, Taylor-linearized); associations are odds ratios (OR) "
        "from design-weighted logistic regression, mutually adjusted, and are "
        "\\emph{not} causal. Depressed mood is a PHQ-9 screen used here as the "
        "available psychological-distress proxy (NHANES lacks a validated "
        "perceived-stress instrument); per the study DAG it is a mediator, so its "
        "OR is a mediator-level association. Generated by "
        "\\texttt{code/src/nhanes\\_analysis.py}. "
        "$^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}",
        "\\label{tab:results}", "\\small", "\\begin{tabular}{lcc}", "\\toprule",
        " & Tinnitus & Hearing loss ($>$25 dB HL) \\\\", "\\midrule",
        f"Prevalence (95\\% CI) & {fmt_prev(pv.get('tinnitus'))} & "
        f"{fmt_prev(pv.get('hearing_loss'))} \\\\",
        "\\midrule",
        "\\multicolumn{3}{l}{\\emph{Adjusted associations, OR (95\\% CI)}} \\\\",
        f"\\quad Occupational noise & {cell(at,'occ_noise')} & {cell(ah,'occ_noise')} \\\\",
        f"\\quad Depressed mood (PHQ-9$\\geq$10) & {cell(at,'depressed')} & {cell(ah,'depressed')} \\\\",
        f"\\quad Age (per year) & {cell(at,'age')} & {cell(ah,'age')} \\\\",
        f"\\quad Female sex & {cell(at,'sex')} & {cell(ah,'sex')} \\\\",
        "\\midrule",
        f"Analytic $N$ (associations) & {nt} & {nh} \\\\",
    ]
    dep = (pv.get("depressed") or {})
    if dep:
        lines.append("\\midrule")
        lines.append(f"\\multicolumn{{3}}{{l}}{{Depression (PHQ-9$\\geq$10) "
                     f"prevalence: {fmt_prev(dep)}, $N={dep.get('n','--')}$}} \\\\")
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

    try:
        import statsmodels.api as _sm  # noqa: F401
    except Exception:
        print("\n*** WARNING: statsmodels is not installed, so association odds "
              "ratios (assoc_*) will be null. Install it to get associations:\n"
              "      python -m venv .venv && . .venv/bin/activate && "
              "pip install statsmodels\n"
              "  (or:  pip install --break-system-packages statsmodels)\n")

    res = run_analysis(df)
    res["cycles"] = args.cycles
    res["n_total_rows"] = int(len(df))
    if res.get("assoc_tinnitus") is None:
        print("NOTE: assoc_tinnitus is null (statsmodels missing or too few "
              "complete cases for the adjusted model).")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    if args.latex:
        Path(args.latex).write_text(to_latex(res), encoding="utf-8")
        print(f"Wrote {args.latex}")
    print(json.dumps(res.get("prevalence", {}), indent=2))


if __name__ == "__main__":
    main()
