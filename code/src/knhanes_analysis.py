"""Real KNHANES survey-weighted analysis for STARS (primary development cohort).

KNHANES is the PRIMARY development dataset because, unlike NHANES, it carries a
general perceived-stress item --- so this is where STARS's primary exposure
(perceived stress) is actually tested. KNHANES microdata require official KDCA
approval and cannot be redistributed; this loader is mapping-driven so it is
ready to run once approved files and the codebook-verified mapping are supplied.

It reuses the SAME validated design-based estimators as the NHANES pipeline
(``svy_mean``, ``svy_logistic``, ``to_latex``) so both cohorts are analyzed
identically. Provide files under ``code/data/raw/knhanes/<cycle>/`` and complete
``config/knhanes_mapping.yaml``, then::

    python src/knhanes_analysis.py --mapping config/knhanes_mapping.yaml \
        --data-dir data/raw/knhanes --cycles 2010 2011 2012 \
        --out outputs/knhanes_results.json \
        --latex ../paper/tables/table_results_knhanes.tex \
        --latex-extended ../paper/tables/table_extended_knhanes.tex

Estimates are survey-weighted with Taylor-linearized 95% CIs; associations are
design-based odds ratios and are not causal.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yaml

# Reuse the validated estimators from the NHANES module (same statistics).
from nhanes_analysis import svy_mean, svy_logistic


def _read_sas(path: Path) -> pd.DataFrame:
    """Read a KNHANES .sas7bdat file robustly.

    Real KNHANES files use Korean (CP949/EUC-KR) labels and sometimes SAS
    compression that pandas cannot decode, so we try pyreadstat first (ReadStat C
    library; auto-detects encoding and handles compression) and fall back to
    pandas with a few encodings. Variable NAMES (BP1, HtE_1, O_R_500, ...) are
    ASCII and analysis uses numeric codes, so label encoding does not affect
    results.
    """
    try:
        import pyreadstat
        df, _ = pyreadstat.read_sas7bdat(str(path))
        return df
    except ImportError:
        pass  # pyreadstat not installed; fall back to pandas
    except Exception:
        pass  # pyreadstat present but failed; try pandas
    last = None
    for enc in ("cp949", "euc-kr", "latin-1"):
        try:
            return pd.read_sas(path, format="sas7bdat", encoding=enc)
        except Exception as e:
            last = e
    raise RuntimeError(
        f"Could not read {path}. Install the robust reader with "
        f"`pip install --break-system-packages pyreadstat`. Last pandas error: {last}")


def _find_id_col(df: pd.DataFrame) -> str:
    """Return the person-id column, tolerating case.

    KNHANES varies the person-id case across files/years: the 2010 기본DB uses
    ``ID`` while 2011-2012 use ``id``, and the ENT files use ``ID``.
    """
    for cand in ("id", "ID"):
        if cand in df.columns:
            return cand
    low = {c.lower(): c for c in df.columns}
    if "id" in low:
        return low["id"]
    raise KeyError("No person-id column (id/ID) found for the KNHANES merge.")


def load_cycle(cycle: str, data_dir: Path, mapping: dict) -> pd.DataFrame:
    finfo = mapping["files"].get(cycle)
    if not finfo:
        raise KeyError(f"No file entry for cycle {cycle} in mapping['files'].")
    path = data_dir / cycle / finfo["exam"]
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Place the KNHANES 기본DB (HN{cycle[2:]}_ALL) file there "
            f"and complete config/knhanes_mapping.yaml.")
    df = _read_sas(path)

    # The hearing outcomes (audiometry + tinnitus + noise) live in the SEPARATE
    # 이비인후검사 (ENT) file, keyed by the same person id. Merge it in here so the
    # rest of the pipeline sees one frame per cycle.
    ent_name = finfo.get("ent")
    if ent_name and not str(ent_name).startswith("<"):
        ent_path = data_dir / cycle / ent_name
        if not ent_path.exists():
            raise FileNotFoundError(
                f"Missing ENT/audiometry file {ent_path}. It carries the hearing "
                f"outcomes; download the '이비인후검사' (HN{cycle[2:]}_ENT) file.")
        ent = _read_sas(ent_path)
        df = df.rename(columns={_find_id_col(df): "id"})
        k_ent = _find_id_col(ent)
        ent = ent.drop_duplicates(subset=[k_ent])
        keep = [k_ent] + [c for c in ent.columns if c not in df.columns and c != k_ent]
        ent = ent[keep].rename(columns={k_ent: "id"})
        n0 = len(df)
        df = df.merge(ent, on="id", how="left")
        if len(df) != n0:
            raise RuntimeError(f"ENT merge changed row count {n0}->{len(df)} for {cycle}.")

    df["cycle"] = cycle
    return df


def _get(df: pd.DataFrame, name) -> Optional[pd.Series]:
    if not name or name == "<FILL>":
        return None
    return df[name] if name in df.columns else None


def derive_variables(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    m = mapping
    out = pd.DataFrame(index=df.index)
    out["cycle"] = df.get("cycle")
    out["age"] = _get(df, m["common"]["age"])
    sex = _get(df, m["common"]["sex"])
    out["sex"] = (sex == 2).astype(float) if sex is not None else np.nan  # 1=female
    out["weight"] = _get(df, m["survey_design"]["weight"])
    out["strata"] = _get(df, m["survey_design"]["strata"])
    out["psu"] = _get(df, m["survey_design"]["psu"])

    # PRIMARY exposure: perceived stress (dichotomized high vs low).
    ps = _get(df, m["exposure"]["perceived_stress"])
    if ps is not None:
        hi = set(m["exposure"]["stress_high_values"])
        out["perceived_stress"] = ps.apply(
            lambda v: 1.0 if v in hi else (np.nan if pd.isna(v) else 0.0))

    # SES covariates for the fully-adjusted sensitivity model (reviewer #4).
    # Education and household income are treated as ordinal integers.
    edu = _get(df, m["common"].get("education"))
    if edu is not None:
        out["education"] = pd.to_numeric(edu, errors="coerce")
    inc = _get(df, m["common"].get("income"))
    if inc is not None:
        out["income"] = pd.to_numeric(inc, errors="coerce")

    # Optional smoking / cardiometabolic flags (skipped if left <FILL>).
    cx = m.get("covariates_extended", {})
    def _binary(name_key, yes_key, out_name):
        col = _get(df, cx.get(name_key))
        yes = set(cx.get(yes_key, []) or [])
        if col is not None and yes:
            out[out_name] = col.apply(
                lambda v: 1.0 if v in yes else (np.nan if pd.isna(v) else 0.0))
    _binary("smoking_current", "smoking_yes_values", "smoking")
    _binary("hypertension", "hypertension_yes_values", "hypertension")
    _binary("diabetes", "diabetes_yes_values", "diabetes")

    # Mediators
    phq_items = [c for c in m["mediators"].get("depression_phq9_items", []) if c in df]
    if phq_items:
        phq = df[phq_items].sum(axis=1, min_count=len(phq_items))
        out["depressed"] = np.where(phq.notna(), (phq >= 10).astype(float), np.nan)
    else:
        dep = _get(df, m["mediators"].get("depressed_2wk"))
        if dep is not None:
            out["depressed"] = dep.map({1: 1.0, 2: 0.0})
    sleep = _get(df, m["mediators"].get("sleep_hours"))
    if sleep is not None:
        out["sleep_hours"] = sleep

    # Outcomes
    tin = _get(df, m["outcomes"]["tinnitus_item"])
    if tin is not None:
        yes = set(m["outcomes"]["tinnitus_yes_values"])
        no = set(m["outcomes"].get("tinnitus_no_values", []))
        if no:  # explicit yes/no; anything else (8=비해당, 9=무응답, ...) is missing
            out["tinnitus"] = tin.apply(
                lambda v: 1.0 if v in yes else (0.0 if v in no else np.nan))
        else:
            out["tinnitus"] = tin.apply(
                lambda v: 1.0 if v in yes else (np.nan if pd.isna(v) else 0.0))
    both = _get(df, m["outcomes"].get("bothersome_item"))
    if both is not None:
        byes = set(m["outcomes"].get("bothersome_yes_values", []))
        bno = set(m["outcomes"].get("bothersome_no_values", []))
        if bno:  # explicit yes/no; 무응답(9) and anything else -> missing
            out["bothersome_tinnitus"] = both.apply(
                lambda v: 1.0 if v in byes else (0.0 if v in bno else np.nan))
        else:
            out["bothersome_tinnitus"] = both.apply(
                lambda v: 1.0 if v in byes else (np.nan if pd.isna(v) else 0.0))
        # NON-BOTHERSOME tinnitus vs no tinnitus (M1 reverse-causation
        # sensitivity): bothersome tinnitus is itself a stressor and drives the
        # strongest feedback loop, so restricting cases to NON-bothersome tinnitus
        # (tinnitus present but not annoying) weakens the reverse-causation
        # pathway. If the stress association persists here, it partially blunts
        # the reverse-causation critique. Controls = no tinnitus; bothersome
        # cases are excluded (set missing).
        if "tinnitus" in out:
            tin01 = out["tinnitus"]
            both01 = out["bothersome_tinnitus"]
            out["nonbothersome_tinnitus"] = np.where(
                tin01 == 0, 0.0,
                np.where((tin01 == 1) & (both01 == 0), 1.0, np.nan))
    occ = _get(df, m["outcomes"]["occupational_noise"])
    if occ is not None:
        out["occ_noise"] = occ.map({1: 1.0, 2: 0.0})

    # Audiometry -> better/worse-ear speech-frequency PTA and hearing loss
    inval = m["audiometry"].get("invalid_threshold_codes", [])
    freqs = m["speech_freqs"]
    rvars = [m["audiometry"][f][0] for f in freqs]
    lvars = [m["audiometry"][f][1] for f in freqs]
    cut = m["analysis"]["hearing_loss_cutoff_db"]
    if all(v in df.columns for v in rvars + lvars):
        rr = df[rvars].replace({c: np.nan for c in inval}).mean(axis=1)
        ll = df[lvars].replace({c: np.nan for c in inval}).mean(axis=1)
        out["better_ear_pta"] = np.minimum(rr, ll)
        out["worse_ear_pta"] = np.maximum(rr, ll)
        out["hearing_loss"] = np.where(
            out["better_ear_pta"].notna(),
            (out["better_ear_pta"] > cut).astype(float), np.nan)
        # Worse-ear speech-frequency hearing loss (unilateral/asymmetric-sensitive,
        # relevant to the SSNHL motivation, per Mo1). Defined on the worse ear.
        out["worse_ear_hearing_loss"] = np.where(
            out["worse_ear_pta"].notna(),
            (out["worse_ear_pta"] > cut).astype(float), np.nan)

    # High-frequency PTA (3/4/6 kHz) where noise damage shows first (Mo1). Better-
    # ear high-frequency hearing loss is a prespecified sensitivity definition.
    hf = m.get("high_freqs", [])
    hfr = [m["audiometry"][f][0] for f in hf if f in m.get("audiometry", {})]
    hfl = [m["audiometry"][f][1] for f in hf if f in m.get("audiometry", {})]
    if hfr and hfl and all(v in df.columns for v in hfr + hfl):
        rr_hf = df[hfr].replace({c: np.nan for c in inval}).mean(axis=1)
        ll_hf = df[hfl].replace({c: np.nan for c in inval}).mean(axis=1)
        out["better_ear_hf_pta"] = np.minimum(rr_hf, ll_hf)
        out["hf_hearing_loss"] = np.where(
            out["better_ear_hf_pta"].notna(),
            (out["better_ear_hf_pta"] > cut).astype(float), np.nan)

    # Tympanometry: normal middle ear in BOTH ears, for a conductive-exclusion
    # sensitivity (KNHANES has air-conduction thresholds but no bone conduction /
    # air-bone gap). 0=normal, 1/2=abnormal, 8/9=missing.
    tv = m.get("tympanometry")
    if tv and all(v in df.columns for v in tv):
        nv = m.get("tympanometry_normal_value", 0)
        valid = df[tv[0]].isin([0, 1, 2]) & df[tv[1]].isin([0, 1, 2])
        both_normal = (df[tv[0]] == nv) & (df[tv[1]] == nv)
        out["tymp_normal"] = np.where(valid, both_normal.astype(float), np.nan)
    return out


def benjamini_hochberg(pvals: Dict[str, float]) -> Dict[str, float]:
    """Benjamini-Hochberg FDR-adjusted q-values for a dict of {name: p}.

    Controls the false-discovery rate across the prespecified *secondary*
    contrasts (Methods) so borderline sensitivity results are not over-read.
    Returns {name: q} with the standard monotone (step-up) correction.
    """
    items = [(k, v) for k, v in pvals.items() if v is not None and np.isfinite(v)]
    m = len(items)
    if m == 0:
        return {}
    order = sorted(range(m), key=lambda i: items[i][1])
    raw = [items[order[r]][1] * m / (r + 1) for r in range(m)]
    q = [0.0] * m
    running = 1.0
    for r in range(m - 1, -1, -1):            # enforce monotonicity from the top
        running = min(running, raw[r])
        q[r] = running
    return {items[order[r]][0]: q[r] for r in range(m)}


def run_analysis(df: pd.DataFrame, mapping: dict) -> dict:
    a = mapping["analysis"]
    # Domain (subpopulation) estimation: retain the FULL design and treat the
    # 40--69 band as the analytic domain, instead of subsetting before variance
    # estimation (which distorts the stratum/PSU structure and the SEs). Single-
    # PSU strata use the conservative centering option inside the estimators.
    dom = ((df["age"] >= a["age_min"]) & (df["age"] <= a["age_max"])).to_numpy()
    res: Dict[str, object] = {"n_analytic": int(dom.sum()),
                              "age_range": [a["age_min"], a["age_max"]]}

    def prev(col):
        if col not in df:
            return None
        e = svy_mean(df[col].to_numpy(), df["weight"].to_numpy(),
                     df["strata"].to_numpy(), df["psu"].to_numpy(), domain=dom)
        return {"prevalence": e.estimate, "se": e.se,
                "ci": [e.ci_low, e.ci_high], "n": e.n}

    res["prevalence"] = {k: prev(k) for k in
                         ["tinnitus", "bothersome_tinnitus", "hearing_loss",
                          "worse_ear_hearing_loss", "hf_hearing_loss",
                          "perceived_stress", "depressed"]}

    # PRIMARY association: perceived stress -> tinnitus / hearing loss,
    # minimal sufficient adjustment set (age, sex, occupational noise).
    base = [p for p in ["perceived_stress", "occ_noise", "age", "sex"] if p in df]
    have_core = {"perceived_stress", "age", "sex"}.issubset(df.columns)

    def logit(outcome, preds):
        return svy_logistic(df, outcome, preds, "weight", "strata", "psu", domain=dom)

    if "tinnitus" in df and have_core:
        res["assoc_tinnitus"] = logit("tinnitus", base)
    if "hearing_loss" in df and have_core:
        res["assoc_hearing_loss"] = logit("hearing_loss", base)

    # --- Prespecified secondary/sensitivity models brought INTO the analysis ---
    # (M2, Mo1): report these in the manuscript, not "only in the repository".

    # (a) EXTENDED (mediator-adjusted) tinnitus model: base + depressed mood.
    #     Interpreted as a mediator-adjusted (NOT confounder-adjusted) estimate.
    if "tinnitus" in df and have_core and "depressed" in df:
        res["assoc_tinnitus_extended"] = logit("tinnitus", base + ["depressed"])

    # (b) HEARING-LOSS-ADJUSTED tinnitus model: does stress->tinnitus survive
    #     adjustment for audiometric hearing loss (a strong tinnitus correlate)?
    if "tinnitus" in df and have_core and "hearing_loss" in df:
        res["assoc_tinnitus_hearing_adj"] = logit("tinnitus", base + ["hearing_loss"])

    # (b2) FULLY-ADJUSTED tinnitus model (reviewer #4): base + depressed mood +
    #      whatever conventional covariates are available (SES: education, income;
    #      and, if mapped, smoking, hypertension, diabetes). Any covariate absent
    #      from the derived frame is simply omitted, so this still runs SES-adjusted.
    extra = [c for c in ["depressed", "education", "income",
                         "smoking", "hypertension", "diabetes"] if c in df]
    if "tinnitus" in df and have_core and extra:
        res["assoc_tinnitus_fulladj"] = logit("tinnitus", base + extra)
        res["fulladj_covariates"] = extra

    # (c) EXTENDED (mediator-adjusted) hearing-loss model: base + depressed mood.
    if "hearing_loss" in df and have_core and "depressed" in df:
        res["assoc_hearing_loss_extended"] = logit("hearing_loss", base + ["depressed"])

    # (d) WORSE-EAR hearing loss (unilateral/asymmetric-sensitive; Mo1).
    if "worse_ear_hearing_loss" in df and have_core:
        res["assoc_hearing_loss_worse"] = logit("worse_ear_hearing_loss", base)

    # (e) HIGH-FREQUENCY (3/4/6 kHz) hearing loss (noise-damage-sensitive; Mo1).
    if "hf_hearing_loss" in df and have_core:
        res["assoc_hearing_loss_hf"] = logit("hf_hearing_loss", base)

    # (f) BOTHERSOME tinnitus (a distinct endpoint) and (g) NON-BOTHERSOME
    #     tinnitus vs no tinnitus (M1 reverse-causation sensitivity).
    if "bothersome_tinnitus" in df and have_core:
        res["assoc_bothersome_tinnitus"] = logit("bothersome_tinnitus", base)
    if "nonbothersome_tinnitus" in df and have_core:
        res["assoc_nonbothersome_tinnitus"] = logit("nonbothersome_tinnitus", base)

    # (h) CONDUCTIVE-EXCLUSION sensitivity: restrict to participants with NORMAL
    #     tympanometry in both ears, since KNHANES lacks bone conduction to
    #     compute an air-bone gap (addresses conductive-contamination concern).
    if "tymp_normal" in df:
        dom_t = dom & (df["tymp_normal"].to_numpy() == 1)
        def logit_t(outcome, preds):
            return svy_logistic(df, outcome, preds, "weight", "strata", "psu", domain=dom_t)
        if "hearing_loss" in df and have_core:
            res["assoc_hearing_loss_tympnorm"] = logit_t("hearing_loss", base)
        if "tinnitus" in df and have_core:
            res["assoc_tinnitus_tympnorm"] = logit_t("tinnitus", base)

    # Multiplicity: Benjamini-Hochberg FDR across the prespecified SECONDARY
    # perceived-stress contrasts (the two primary endpoints -- tinnitus and
    # better-ear hearing loss -- are the confirmatory H1 test and are excluded).
    secondary = {
        "tinnitus_extended": "assoc_tinnitus_extended",
        "tinnitus_hearing_adj": "assoc_tinnitus_hearing_adj",
        "tinnitus_fulladj": "assoc_tinnitus_fulladj",
        "hearing_loss_extended": "assoc_hearing_loss_extended",
        "hearing_loss_worse": "assoc_hearing_loss_worse",
        "hearing_loss_hf": "assoc_hearing_loss_hf",
        "bothersome_tinnitus": "assoc_bothersome_tinnitus",
        "nonbothersome_tinnitus": "assoc_nonbothersome_tinnitus",
    }
    pvals = {name: res[key]["perceived_stress"]["p_value"]
             for name, key in secondary.items()
             if res.get(key) and "perceived_stress" in res[key]}
    if pvals:
        res["fdr_secondary_perceived_stress"] = benjamini_hochberg(pvals)

    # Exploratory mediation (difference method on the log-odds of perceived
    # stress): the share of the crude stress->tinnitus association attenuated by
    # adjusting for depressed mood. Interpreted cautiously -- cross-sectional
    # mediation assumptions, and logistic non-collapsibility, apply.
    at, ate = res.get("assoc_tinnitus"), res.get("assoc_tinnitus_extended")
    if at and ate and "perceived_stress" in at and "perceived_stress" in ate:
        import math
        bc = math.log(at["perceived_stress"]["odds_ratio"])
        ba = math.log(ate["perceived_stress"]["odds_ratio"])
        res["mediation_depressed_tinnitus"] = {
            "or_crude": at["perceived_stress"]["odds_ratio"],
            "or_mediator_adjusted": ate["perceived_stress"]["odds_ratio"],
            "prop_attenuated": (1.0 - ba / bc) if bc else None,
            "method": "difference (log-odds), exploratory",
        }

    return res


def to_latex(res: dict) -> str:
    """KNHANES results table with perceived stress as the primary exposure."""
    def fmt_prev(x):
        return ("--" if not x else
                f"{100*x['prevalence']:.1f}\\% ({100*x['ci'][0]:.1f}--{100*x['ci'][1]:.1f})")

    def stars(p):
        return "" if p is None else (
            "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "")

    def cell(a, k):
        if not a or k not in a:
            return "--"
        o = a[k]
        return f"{o['odds_ratio']:.2f} ({o['ci_low']:.2f}--{o['ci_high']:.2f}){stars(o.get('p_value'))}"

    at, ah = res.get("assoc_tinnitus"), res.get("assoc_hearing_loss")
    pv = res.get("prevalence", {})
    lines = [
        "\\begin{table}[htbp]", "\\centering",
        "\\caption{\\textbf{Real KNHANES results} (Korean adults 40--69). "
        "Primary development cohort with the perceived-stress exposure. "
        "Prevalence is design-based (survey-weighted, Taylor-linearized); "
        "associations are mutually adjusted design-based odds ratios and are "
        "\\emph{not} causal. Generated by \\texttt{code/src/knhanes\\_analysis.py}. "
        "$^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}",
        "\\label{tab:results_knhanes}", "\\small", "\\begin{tabular}{lcc}", "\\toprule",
        " & Tinnitus & Hearing loss ($>$25 dB HL) \\\\", "\\midrule",
        f"Prevalence (95\\% CI) & {fmt_prev(pv.get('tinnitus'))} & {fmt_prev(pv.get('hearing_loss'))} \\\\",
        "\\midrule",
        "\\multicolumn{3}{l}{\\emph{Adjusted associations, OR (95\\% CI)}} \\\\",
        f"\\quad Perceived stress (high) & {cell(at,'perceived_stress')} & {cell(ah,'perceived_stress')} \\\\",
        f"\\quad Occupational noise & {cell(at,'occ_noise')} & {cell(ah,'occ_noise')} \\\\",
        f"\\quad Age (per year) & {cell(at,'age')} & {cell(ah,'age')} \\\\",
        f"\\quad Female sex & {cell(at,'sex')} & {cell(ah,'sex')} \\\\",
        "\\bottomrule", "\\end{tabular}", "\\end{table}", "",
    ]
    return "\n".join(lines)


def to_latex_extended(res: dict) -> str:
    """Extended / sensitivity table isolating the perceived-stress OR across
    model specifications (mediator-adjusted, hearing-loss-adjusted, worse-ear,
    high-frequency). Brings the prespecified secondary analyses INTO the paper."""
    def stars(p):
        return "" if p is None else (
            "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "")

    def cell(key, param="perceived_stress"):
        a = res.get(key)
        if not a or param not in a:
            return "--"
        o = a[param]
        return (f"{o['odds_ratio']:.2f} ({o['ci_low']:.2f}--{o['ci_high']:.2f})"
                f"{stars(o.get('p_value'))}")

    def nof(key):
        a = res.get(key)
        return str(a.get("_n", "--")) if a else "--"

    rows = [
        ("Tinnitus --- minimal-sufficient (primary)", "assoc_tinnitus"),
        ("\\quad + depressed mood (mediator-adjusted)", "assoc_tinnitus_extended"),
        ("\\quad + audiometric hearing loss", "assoc_tinnitus_hearing_adj"),
        ("\\quad + SES/comorbidity (fully adjusted)", "assoc_tinnitus_fulladj"),
        ("Hearing loss, better ear --- minimal-sufficient", "assoc_hearing_loss"),
        ("\\quad + depressed mood (mediator-adjusted)", "assoc_hearing_loss_extended"),
        ("Hearing loss, worse ear --- minimal-sufficient", "assoc_hearing_loss_worse"),
        ("Hearing loss, high-freq (3/4/6\\,kHz) --- minimal-sufficient",
         "assoc_hearing_loss_hf"),
        ("Hearing loss, normal tympanometry (conductive-excluded)",
         "assoc_hearing_loss_tympnorm"),
        ("Bothersome tinnitus --- minimal-sufficient", "assoc_bothersome_tinnitus"),
        ("Non-bothersome tinnitus vs none (reverse-causation sensitivity)",
         "assoc_nonbothersome_tinnitus"),
    ]
    body = "\n".join(
        f"{label} & {cell(key)} & {nof(key)} \\\\" for label, key in rows)
    return "\n".join([
        "\\begin{table}[htbp]", "\\centering",
        "\\caption{\\textbf{Extended and sensitivity models (KNHANES, adults "
        "40--69).} Perceived-stress odds ratio (95\\% CI) across prespecified "
        "specifications, isolating the robustness of the primary exposure. Rows "
        "add the mediator (depressed mood) or audiometric hearing loss to the "
        "minimal-sufficient set (perceived stress, occupational noise, age, sex), "
        "and vary the hearing-loss outcome definition (better-ear, worse-ear, "
        "high-frequency). All are design-based associations, not causal effects; "
        "mediator-adjusted rows are interpreted as mediator- (not confounder-) "
        "adjusted. Bothersome tinnitus (moderate/severe annoyance) is modeled "
        "versus all others; non-bothersome tinnitus (present but not annoying) "
        "versus no tinnitus, excluding bothersome cases. Secondary contrasts are "
        "Benjamini--Hochberg false-discovery-rate controlled (reported in text). "
        "Generated by \\texttt{code/src/knhanes\\_analysis.py}. "
        "$^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.}",
        "\\label{tab:results_knhanes_extended}", "\\small",
        "\\begin{tabular}{lcc}", "\\toprule",
        "Model specification & Perceived stress, OR (95\\% CI) & $N$ \\\\",
        "\\midrule", body, "\\bottomrule", "\\end{tabular}", "\\end{table}", "",
    ])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", default="config/knhanes_mapping.yaml")
    ap.add_argument("--data-dir", default="data/raw/knhanes")
    ap.add_argument("--cycles", nargs="+", default=["2010", "2011", "2012"])
    ap.add_argument("--out", default="outputs/knhanes_results.json")
    ap.add_argument("--latex", default=None)
    ap.add_argument("--latex-extended", default=None,
                    help="path to write the extended/sensitivity model table")
    ap.add_argument("--dump-analytic", default=None,
                    help="write the derived analytic frame to CSV for independent "
                         "SE reproduction (e.g. R survey / samplics; see "
                         "src/reproduce_survey.R)")
    args = ap.parse_args()
    mapping = yaml.safe_load(Path(args.mapping).read_text(encoding="utf-8"))
    data_dir = Path(args.data_dir)

    frames = [derive_variables(load_cycle(c, data_dir, mapping), mapping)
              for c in args.cycles]
    df = pd.concat(frames, ignore_index=True)

    # KDCA pooling rule: when combining K survey years, divide the integrated
    # weight by K so the pooled weights sum to a single-year population.
    n_cyc = len(args.cycles)
    if n_cyc > 1 and "weight" in df:
        df["weight"] = df["weight"] / n_cyc
        print(f"Pooled {n_cyc} cycles: divided survey weight by {n_cyc}.")

    print("Derived-variable coverage (non-null counts):")
    for v in ["perceived_stress", "tinnitus", "hearing_loss", "better_ear_pta",
              "occ_noise", "depressed", "age", "sex", "weight"]:
        n = int(df[v].notna().sum()) if v in df else 0
        flag = "" if (v in df and n > 0) else "   <-- MISSING (fill mapping / check codebook)"
        print(f"  {v:16s}: {n}{flag}")

    if args.dump_analytic:
        Path(args.dump_analytic).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.dump_analytic, index=False)
        print(f"Wrote analytic frame for SE reproduction -> {args.dump_analytic}")

    res = run_analysis(df, mapping)
    res["cycles"] = args.cycles
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    if args.latex:
        Path(args.latex).write_text(to_latex(res), encoding="utf-8")
        print(f"Wrote {args.latex}")
    if args.latex_extended:
        Path(args.latex_extended).write_text(to_latex_extended(res), encoding="utf-8")
        print(f"Wrote {args.latex_extended}")
    print(json.dumps(res.get("prevalence", {}), indent=2))


if __name__ == "__main__":
    main()
