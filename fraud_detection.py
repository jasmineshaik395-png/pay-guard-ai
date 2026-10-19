"""Educational anomaly-detection helper for PayGuard AI.

This is an unsupervised Isolation Forest demo, not a validated production fraud
detector. It needs representative transaction features and should never make
real payment approval/decline decisions without proper evaluation.
"""
from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ["amount", "country_mismatch", "failed_attempts"]


def _prepare(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    if "amount" not in frame:
        frame["amount"] = 0
    if "country_mismatch" not in frame:
        frame["country_mismatch"] = 0
    if "failed_attempts" not in frame:
        frame["failed_attempts"] = 0

    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce").fillna(0)
    frame["failed_attempts"] = pd.to_numeric(
        frame["failed_attempts"], errors="coerce"
    ).fillna(0)

    mismatch = frame["country_mismatch"]
    if mismatch.dtype == object:
        frame["country_mismatch"] = (
            mismatch.astype(str).str.strip().str.lower()
            .isin(["yes", "true", "1", "y"]).astype(int)
        )
    else:
        frame["country_mismatch"] = pd.to_numeric(
            mismatch, errors="coerce"
        ).fillna(0).astype(int)

    return frame[FEATURES].astype(float)


def score_transactions(data: pd.DataFrame, contamination: float = 0.1) -> pd.DataFrame:
    """Return a copy with anomaly_label, anomaly_score, and model_name columns."""
    if data.empty:
        result = data.copy()
        result["anomaly_label"] = []
        result["anomaly_score"] = []
        result["model_name"] = []
        return result

    features = _prepare(data)
    model = IsolationForest(
        n_estimators=200,
        contamination=min(max(float(contamination), 0.01), 0.49),
        random_state=42,
    )
    model.fit(features)
    predictions = model.predict(features)  # -1 = anomaly, 1 = inlier
    raw_scores = model.decision_function(features)

    result = data.copy()
    result["anomaly_label"] = ["Potential anomaly" if p == -1 else "Typical pattern"
                               for p in predictions]
    # Higher score means more anomalous for easier interpretation.
    result["anomaly_score"] = (-raw_scores).round(4)
    result["model_name"] = "IsolationForest (unsupervised demo)"
    return result
