"""Dataset loaders and harmonization helpers.

KNHANES raw files are not redistributed. Place official KDCA files under
`data/raw/knhanes/`. NHANES public-use XPT files can be downloaded separately
from CDC and placed under `data/raw/nhanes/`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import numpy as np
import pandas as pd


def read_table(path: Path) -> pd.DataFrame:
    """Read CSV, SAS7BDAT, SAV, or XPT files into pandas."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".sas7bdat", ".xpt"}:
        return pd.read_sas(path, format="xport" if suffix == ".xpt" else "sas7bdat")
    if suffix == ".sav":
        import pyreadstat
        df, _ = pyreadstat.read_sav(str(path))
        return df
    raise ValueError(f"Unsupported file format: {path}")


def calculate_pta(df: pd.DataFrame, ear_prefix: str, freqs: Iterable[str]) -> pd.Series:
    """Calculate pure-tone average from available frequency columns."""
    cols = [f"{ear_prefix}_{freq}" for freq in freqs if f"{ear_prefix}_{freq}" in df.columns]
    if not cols:
        return pd.Series(np.nan, index=df.index)
    return df[cols].mean(axis=1, skipna=True)


def harmonize_generic(df: pd.DataFrame, mapping: Dict[str, str], dataset_name: str) -> pd.DataFrame:
    """Rename columns into the HEAR-WORK common schema.

    mapping maps common_name -> dataset_specific_column.
    Missing fields are filled with NaN to make model code stable.
    """
    out = pd.DataFrame(index=df.index)
    for common_name, source_col in mapping.items():
        out[common_name] = df[source_col] if source_col in df.columns else np.nan
    out["dataset"] = dataset_name
    return out


def derive_hearing_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive PTA-based features after harmonization."""
    out = df.copy()
    if {"left_pta", "right_pta"}.issubset(out.columns):
        out["better_ear_pta"] = out[["left_pta", "right_pta"]].min(axis=1)
        out["worse_ear_pta"] = out[["left_pta", "right_pta"]].max(axis=1)
        out["asymmetric_loss"] = (out["worse_ear_pta"] - out["better_ear_pta"] >= 15).astype("float")
        out["hearing_loss_pta"] = (out["better_ear_pta"] >= 26).astype("float")
    return out
