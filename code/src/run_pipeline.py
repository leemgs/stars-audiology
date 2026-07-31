"""HEAR-WORK AI public-data pipeline starter.

The script demonstrates the intended workflow without redistributing raw data.
When official KNHANES/NHANES files and a mapping file are supplied, replace the
placeholder data-loading block with actual harmonization calls.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import yaml
import numpy as np
import pandas as pd

from modeling import train_and_evaluate


def make_synthetic_smoke_data(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create synthetic data only for code smoke testing.

    Do not use synthetic results as manuscript findings.
    """
    rng = np.random.default_rng(seed)
    def one(n: int, dataset: str) -> pd.DataFrame:
        age = rng.integers(40, 61, n)
        stress = rng.integers(1, 5, n)
        noise = rng.integers(0, 2, n)
        sex = rng.choice(["female", "male"], n)
        base = -4.0 + 0.04 * age + 0.35 * stress + 0.65 * noise
        tinnitus = rng.binomial(1, 1 / (1 + np.exp(-base)))
        hearing = rng.binomial(1, 1 / (1 + np.exp(-(-5.0 + 0.07 * age + 0.5 * noise))))
        return pd.DataFrame({"dataset": dataset, "age": age, "perceived_stress": stress, "occupational_noise": noise, "sex": sex, "tinnitus_status": tinnitus, "hearing_loss_pta": hearing})
    return one(500, "KNHANES_SYNTHETIC_SMOKE"), one(300, "NHANES_SYNTHETIC_SMOKE")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/study_config.yaml")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(cfg["paths"]["outputs"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # Replace this smoke-test section with actual KNHANES/NHANES harmonized data.
    train, test = make_synthetic_smoke_data()
    numeric = ["age", "perceived_stress", "occupational_noise"]
    categorical = ["sex"]
    metrics_tinnitus = train_and_evaluate(train, test, "tinnitus_status", numeric, categorical, out_dir)
    metrics_hearing = train_and_evaluate(train, test, "hearing_loss_pta", numeric, categorical, out_dir)
    print("Smoke-test metrics. Do not report as scientific results.")
    print(metrics_tinnitus)
    print(metrics_hearing)


if __name__ == "__main__":
    main()
