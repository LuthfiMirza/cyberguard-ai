from __future__ import annotations

import argparse
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from src.data_loader import load_dataset
from src.features import build_feature_dataframe


def evaluate(data_path: str, model_path: str, report_out: str = "reports/classification_report.txt") -> None:
    df = load_dataset(data_path)
    X = build_feature_dataframe(df["url"])
    y = df["label"]

    artifact = joblib.load(model_path)
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]
    X = X[feature_columns]

    y_pred = model.predict(X)
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X)[:, 1]
        roc_auc = roc_auc_score(y, y_score)
    else:
        roc_auc = float("nan")

    report = classification_report(y, y_pred, target_names=["benign", "phishing"])
    metrics = {
        "accuracy": accuracy_score(y, y_pred),
        "precision_phishing": precision_score(y, y_pred, pos_label=1, zero_division=0),
        "recall_phishing": recall_score(y, y_pred, pos_label=1, zero_division=0),
        "f1_phishing": f1_score(y, y_pred, pos_label=1, zero_division=0),
        "roc_auc": roc_auc,
    }

    print("Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
    print("\nClassification report:")
    print(report)
    print("Confusion matrix:")
    print(confusion_matrix(y, y_pred))

    Path(report_out).parent.mkdir(parents=True, exist_ok=True)
    with open(report_out, "w", encoding="utf-8") as file:
        file.write("CyberGuard AI Evaluation Report\n")
        file.write("================================\n\n")
        for key, value in metrics.items():
            file.write(f"{key}: {value:.4f}\n")
        file.write("\nClassification Report\n")
        file.write(report)
    print(f"Saved report to {report_out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CyberGuard AI model")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--report-out", default="reports/classification_report.txt")
    args = parser.parse_args()
    evaluate(args.data, args.model, args.report_out)


if __name__ == "__main__":
    main()
