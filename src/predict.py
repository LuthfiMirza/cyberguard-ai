from __future__ import annotations

import joblib

from src.config import RISK_HIGH_THRESHOLD, RISK_LOW_THRESHOLD
from src.features import build_feature_dataframe, extract_url_features


def get_risk_level(probability: float) -> str:
    if probability < RISK_LOW_THRESHOLD:
        return "Low"
    if probability < RISK_HIGH_THRESHOLD:
        return "Medium"
    return "High"


def predict_url(url: str, model_path: str = "models/cyberguard_model.joblib") -> dict:
    artifact = joblib.load(model_path)
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]

    X = build_feature_dataframe([url])[feature_columns]
    prediction = int(model.predict(X)[0])

    if hasattr(model, "predict_proba"):
        phishing_probability = float(model.predict_proba(X)[0][1])
    else:
        phishing_probability = float(prediction)

    return {
        "url": url,
        "prediction": prediction,
        "label": "phishing/malicious" if prediction == 1 else "benign",
        "phishing_probability": phishing_probability,
        "risk_level": get_risk_level(phishing_probability),
        "features": extract_url_features(url),
    }
