from __future__ import annotations

import argparse
from pathlib import Path

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


def prepare_input(df: pd.DataFrame, artifact: dict) -> pd.DataFrame:
    if "url" not in df.columns:
        raise ValueError("Input must contain a url column")
    working_df = df.copy()
    if "subject" not in working_df.columns:
        working_df["subject"] = ""
    if "body" not in working_df.columns:
        working_df["body"] = ""

    X = build_model_input(working_df)
    input_columns = artifact.get("input_columns")
    if input_columns:
        X = X[input_columns]
    return X


def predict_url(
    url: str,
    model_path: str = "models/cyberguard_model.joblib",
    subject: str = "",
    body: str = "",
) -> dict:
    artifact = joblib.load(model_path)
    model = artifact["model"]

    input_df = pd.DataFrame([{"url": url, "subject": subject, "body": body}])
    X = prepare_input(input_df, artifact)

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
        "probability_phishing": risk_score,
        "phishing_probability": risk_score,
        "risk_level": get_risk_level(risk_score),
        "features": extract_url_features(url),
    }


def predict_batch(
    csv_path: str,
    model_path: str = "models/cyberguard_model.joblib",
    output_path: str = "reports/batch_predictions.csv",
) -> pd.DataFrame:
    artifact = joblib.load(model_path)
    model = artifact["model"]
    df = pd.read_csv(csv_path)
    X = prepare_input(df, artifact)

    predictions = model.predict(X).astype(int)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[:, 1]
    else:
        probabilities = predictions.astype(float)

    results = pd.DataFrame({
        "url": df["url"].astype(str),
        "prediction": predictions,
        "probability_phishing": probabilities,
    })
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)

    benign_count = int((results["prediction"] == 0).sum())
    phishing_count = int((results["prediction"] == 1).sum())
    print(f"Saved batch predictions to {output_path}")
    print(f"Summary: benign={benign_count}, phishing={phishing_count}")
    print("Top 3 highest-risk URLs:")
    for _, row in results.sort_values("probability_phishing", ascending=False).head(3).iterrows():
        print(f"- {row['url']} ({row['probability_phishing']:.4f})")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict phishing risk for a URL or CSV batch")
    parser.add_argument("--url")
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--batch", help="CSV path with url or url,subject,body columns")
    parser.add_argument("--model", default="models/cyberguard_model.joblib")
    parser.add_argument("--output", default="reports/batch_predictions.csv")
    args = parser.parse_args()

    if args.batch:
        predict_batch(args.batch, args.model, args.output)
        return
    if not args.url:
        parser.error("Either --url or --batch is required")

    result = predict_url(args.url, args.model, subject=args.subject, body=args.body)
    print(f"predicted_label: {result['predicted_label']}")
    print(f"risk_score: {result['risk_score']:.4f}")
    print(f"risk_level: {result['risk_level']}")


if __name__ == "__main__":
    main()
