from __future__ import annotations

import argparse
import os
from pathlib import Path

import joblib

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score

from src.data_loader import load_dataset
from src.features import build_model_input


def safe_roc_auc(y, y_score) -> float:
    try:
        return roc_auc_score(y, y_score)
    except ValueError as error:
        print(f"ROC-AUC could not be calculated: {error}")
        return float("nan")


def save_confusion_matrix(matrix, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(5, 4))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["benign", "phishing"],
        yticklabels=["benign", "phishing"],
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def evaluate(data_path: str, model_path: str, report_out: str = "reports/evaluation_report.txt") -> None:
    df = load_dataset(data_path)
    X = build_model_input(df)
    y = df["label"]

    artifact = joblib.load(model_path)
    model = artifact["model"]
    input_columns = artifact.get("input_columns")
    if input_columns:
        X = X[input_columns]

    y_pred = model.predict(X)
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X)[:, 1]
        roc_auc = safe_roc_auc(y, y_score)
    else:
        roc_auc = float("nan")

    matrix = confusion_matrix(y, y_pred, labels=[0, 1])
    report = classification_report(y, y_pred, target_names=["benign", "phishing"], zero_division=0)
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
    print(matrix)

    Path(report_out).parent.mkdir(parents=True, exist_ok=True)
    matrix_out = str(Path(report_out).with_name("confusion_matrix.png"))
    save_confusion_matrix(matrix, matrix_out)
    with open(report_out, "w", encoding="utf-8") as file:
        file.write("CyberGuard AI Evaluation Report\n")
        file.write("================================\n\n")
        for key, value in metrics.items():
            file.write(f"{key}: {value:.4f}\n")
        file.write("\nConfusion Matrix\n")
        file.write(f"{matrix}\n")
        file.write("\nClassification Report\n")
        file.write(report)
    print(f"Saved report to {report_out}")
    print(f"Saved confusion matrix to {matrix_out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CyberGuard AI model")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--report-out", default="reports/evaluation_report.txt")
    args = parser.parse_args()
    evaluate(args.data, args.model, args.report_out)


if __name__ == "__main__":
    main()
