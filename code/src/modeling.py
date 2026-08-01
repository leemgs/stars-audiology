"""Survey-aware baseline analysis and machine-learning risk models."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def calibration_metrics(y_true: np.ndarray, prob: np.ndarray) -> dict:
    """Calibration-in-the-large and calibration slope, reported separately.

    - calibration_in_the_large: mean(predicted) - mean(observed); 0 is ideal.
    - calibration_slope: slope of logit(observed) ~ logit(predicted); 1 is ideal.
      Estimated by a 1-covariate logistic regression on the linear predictor.
    These are the external-validation calibration targets in the protocol.
    """
    y = np.asarray(y_true, dtype=float)
    p = np.clip(np.asarray(prob, dtype=float), 1e-6, 1 - 1e-6)
    citl = float(p.mean() - y.mean())
    slope = float("nan")
    if len(np.unique(y)) > 1:
        lp = np.log(p / (1 - p)).reshape(-1, 1)
        try:
            lr = LogisticRegression(fit_intercept=True, C=1e6, max_iter=1000)
            lr.fit(lp, y.astype(int))
            slope = float(lr.coef_[0][0])
        except Exception:
            slope = float("nan")
    return {"calibration_in_the_large": citl, "calibration_slope": slope}


def build_baseline_pipeline(numeric: List[str], categorical: List[str]) -> Pipeline:
    pre = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), numeric),
            ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
        ]
    )
    return Pipeline([("preprocess", pre), ("clf", LogisticRegression(max_iter=2000))])


def train_and_evaluate(train: pd.DataFrame, test: pd.DataFrame, outcome: str, numeric: List[str], categorical: List[str], out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    features = numeric + categorical
    train2 = train.dropna(subset=[outcome])
    test2 = test.dropna(subset=[outcome])
    pipe = build_baseline_pipeline(numeric, categorical)
    pipe.fit(train2[features], train2[outcome].astype(int))
    prob = pipe.predict_proba(test2[features])[:, 1]
    metrics = {
        "n_train": int(len(train2)),
        "n_test": int(len(test2)),
        "outcome": outcome,
        "roc_auc": float(roc_auc_score(test2[outcome].astype(int), prob)) if test2[outcome].nunique() > 1 else None,
        "pr_auc": float(average_precision_score(test2[outcome].astype(int), prob)) if test2[outcome].nunique() > 1 else None,
        "brier": float(brier_score_loss(test2[outcome].astype(int), prob)) if test2[outcome].nunique() > 1 else None,
    }
    metrics.update(calibration_metrics(test2[outcome].astype(int), prob))
    (out_dir / f"metrics_{outcome}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics
