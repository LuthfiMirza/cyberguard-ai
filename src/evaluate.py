from __future__ import annotations

import argparse
import os
from pathlib import Path

import joblib
import numpy as np

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


def get_transformed_matrix(model, X):
    transformed = model.named_steps["preprocessor"].transform(X)
    if hasattr(transformed, "toarray"):
        return transformed.toarray()
    return np.asarray(transformed)


def get_feature_names(artifact: dict, model) -> list[str]:
    if artifact.get("feature_names"):
        return artifact["feature_names"]
    try:
        names = model.named_steps["preprocessor"].get_feature_names_out()
        return [name.replace("url_features__", "").replace("email_tfidf__", "email:") for name in names]
    except Exception:
        return []


def save_shap_plots(artifact: dict, X, output_dir: str = "reports") -> None:
    try:
        import shap
    except ImportError:
        print("Warning: SHAP is not installed. Skipping SHAP plots.")
        return

    model = artifact["model"]
    classifier = model.named_steps["model"]
    feature_names = get_feature_names(artifact, model)
    if not feature_names:
        print("Warning: feature names unavailable. Skipping SHAP plots.")
        return

    try:
        X_transformed = get_transformed_matrix(model, X)
        sample_size = min(len(X_transformed), 100)
        X_sample = X_transformed[:sample_size]
        model_type = artifact.get("model_type", "")

        if model_type == "logreg" or hasattr(classifier, "coef_"):
            explainer = shap.LinearExplainer(classifier, X_sample)
        elif hasattr(classifier, "feature_importances_"):
            explainer = shap.TreeExplainer(classifier)
        else:
            print("Warning: model type is not supported for SHAP plots. Skipping.")
            return

        shap_values = explainer.shap_values(X_sample)
        if isinstance(shap_values, list):
            shap_values = shap_values[-1]
        if getattr(shap_values, "ndim", 0) == 3:
            shap_values = shap_values[:, :, -1]

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        summary_out = Path(output_dir) / "shap_summary.png"
        beeswarm_out = Path(output_dir) / "shap_beeswarm.png"

        plt.figure()
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names, plot_type="bar", max_display=15, show=False)
        plt.tight_layout()
        plt.savefig(summary_out, bbox_inches="tight")
        plt.close()

        plt.figure()
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names, max_display=15, show=False)
        plt.tight_layout()
        plt.savefig(beeswarm_out, bbox_inches="tight")
        plt.close()

        print(f"Saved SHAP summary to {summary_out}")
        print(f"Saved SHAP beeswarm to {beeswarm_out}")
    except Exception as error:
        print(f"Warning: SHAP plot generation failed: {error}")


def evaluate(data_path: str, model_path: str, report_out: str = "reports/evaluation_report.txt", no_shap: bool = False) -> None:
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

    if not no_shap:
        save_shap_plots(artifact, X, str(Path(report_out).parent))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CyberGuard AI model")
    parser.add_argument("--data", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--report-out", default="reports/evaluation_report.txt")
    parser.add_argument("--no-shap", action="store_true", help="Skip SHAP explanation plots")
    args = parser.parse_args()
    evaluate(args.data, args.model, args.report_out, args.no_shap)


if __name__ == "__main__":
    main()
