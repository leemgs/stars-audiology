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
        --latex ../paper/tables/table_results_knhanes.tex

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
        out["bothersome_tinnitus"] = both.apply(
            lambda v: 1.0 if v in byes else (np.nan if pd.isna(v) else 0.0))
    occ = _get(df, m["outcomes"]["occupational_noise"])
    if occ is not None:
        out["occ_noise"] = occ.map({1: 1.0, 2: 0.0})

    # Audiometry -> better/worse-ear speech-frequency PTA and hearing loss
    inval = m["audiometry"].get("invalid_threshold_codes", [])
    freqs = m["speech_freqs"]
    rvars = [m["audiometry"][f][0] for f in freqs]
    lvars = [m["audiometry"][f][1] for f in freqs]
    if all(v in df.columns for v in rvars + lvars):
        rr = df[rvars].replace({c: np.nan for c in inval}).mean(axis=1)
        ll = df[lvars].replace({c: np.nan for c in inval}).mean(axis=1)
        out["better_ear_pta"] = np.minimum(rr, ll)
        out["worse_ear_pta"] = np.maximum(rr, ll)
        cut = m["analysis"]["hearing_loss_cutoff_db"]
        out["hearing_loss"] = np.where(
            out["better_ear_pta"].notna(),
            (out["better_ear_pta"] > cut).astype(float), np.nan)
    return out


def run_analysis(df: pd.DataFrame, mapping: dict) -> dict:
    a = mapping["analysis"]
    d = df[(df["age"] >= a["age_min"]) & (df["age"] <= a["age_max"])].copy()
    res: Dict[str, object] = {"n_analytic": int(len(d)),
                              "age_range": [a["age_min"], a["age_max"]]}

    def prev(col):
        if col not in d:
            return None
        e = svy_mean(d[col].values, d["weight"].values,
                     d["strata"].values, d["psu"].values)
        return {"prevalence": e.estimate, "se": e.se,
                "ci": [e.ci_low, e.ci_high], "n": e.n}

    res["prevalence"] = {k: prev(k) for k in
                         ["tinnitus", "bothersome_tinnitus", "hearing_loss",
                          "perceived_stress", "depressed"]}

    # PRIMARY association: perceived stress -> tinnitus / hearing loss,
    # minimal sufficient adjustment set (age, sex, occupational noise).
    base = [p for p in ["perceived_stress", "occ_noise", "age", "sex"] if p in d]
    if "tinnitus" in d and {"perceived_stress", "age", "sex"}.issubset(d.columns):
        res["assoc_tinnitus"] = svy_logistic(d, "tinnitus", base,
                                              "weight", "strata", "psu")
    if "hearing_loss" in d and {"perceived_stress", "age", "sex"}.issubset(d.columns):
        res["assoc_hearing_loss"] = svy_logistic(d, "hearing_loss", base,
                                                  "weight", "strata", "psu")
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", default="config/knhanes_mapping.yaml")
    ap.add_argument("--data-dir", default="data/raw/knhanes")
    ap.add_argument("--cycles", nargs="+", default=["2010", "2011", "2012"])
    ap.add_argument("--out", default="outputs/knhanes_results.json")
    ap.add_argument("--latex", default=None)
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

    res = run_analysis(df, mapping)
    res["cycles"] = args.cycles
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    if args.latex:
        Path(args.latex).write_text(to_latex(res), encoding="utf-8")
        print(f"Wrote {args.latex}")
    print(json.dumps(res.get("prevalence", {}), indent=2))


if __name__ == "__main__":
    main()
