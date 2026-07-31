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
    (out_dir / f"metrics_{outcome}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics
