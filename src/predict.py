from __future__ import annotations

import joblib
import pandas as pd

from src.config import RISK_HIGH_THRESHOLD, RISK_LOW_THRESHOLD
from src.features import build_model_input, extract_url_features


def get_risk_level(probability: float) -> str:
    if probability < RISK_LOW_THRESHOLD:
        return "low"
    if probability < RISK_HIGH_THRESHOLD:
        return "medium"
    return "high"


def predict_url(
    url: str,
    model_path: str = "models/cyberguard_model.joblib",
    subject: str = "",
    body: str = "",
) -> dict:
    artifact = joblib.load(model_path)
    model = artifact["model"]

    input_df = pd.DataFrame([{"url": url, "subject": subject, "body": body}])
    X = build_model_input(input_df)
    input_columns = artifact.get("input_columns")
    if input_columns:
        X = X[input_columns]

    prediction = int(model.predict(X)[0])
    if hasattr(model, "predict_proba"):
        risk_score = float(model.predict_proba(X)[0][1])
    else:
        risk_score = float(prediction)

    return {
        "url": url,
        "prediction": prediction,
        "predicted_label": "phishing/malicious" if prediction == 1 else "benign",
        "label": "phishing/malicious" if prediction == 1 else "benign",
        "risk_score": risk_score,
        "phishing_probability": risk_score,
        "risk_level": get_risk_level(risk_score),
        "features": extract_url_features(url),
    }
