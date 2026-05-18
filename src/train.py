from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.data_loader import load_dataset
from src.features import build_model_input

MODEL_ALIASES = {
    "logreg": "logreg",
    "logistic_regression": "logreg",
    "rf": "rf",
    "random_forest": "rf",
    "xgboost": "xgboost",
}


def normalize_model_type(model_type: str) -> str:
    key = model_type.strip().lower()
    if key not in MODEL_ALIASES:
        raise ValueError(f"Unsupported model type: {model_type}")
    return MODEL_ALIASES[key]


def split_dataset(X, y):
    try:
        return train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError as error:
        print(f"Stratified split failed, falling back to regular split: {error}")
        return train_test_split(X, y, test_size=0.2, random_state=42)


def compute_scale_pos_weight(y) -> float:
    negative_count = int((y == 0).sum())
    positive_count = int((y == 1).sum())
    if positive_count == 0:
        return 1.0
    return max(negative_count / positive_count, 1e-6)


def make_classifier(model_type: str, y=None):
    if model_type == "logreg":
        return LogisticRegression(max_iter=1000, class_weight="balanced")
    if model_type == "rf":
        return RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        )
    if model_type == "xgboost":
        try:
            from xgboost import XGBClassifier
        except Exception as error:
            raise RuntimeError(
                "XGBoost is unavailable. On macOS, install OpenMP with `brew install libomp` "
                "then rerun training."
            ) from error
        return XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="logloss",
            scale_pos_weight=compute_scale_pos_weight(y),
            random_state=42,
            n_jobs=1,
        )
    raise ValueError(f"Unsupported model type: {model_type}")


def make_pipeline(model_type: str, numeric_columns: list[str], y=None) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("url_features", StandardScaler(), numeric_columns),
            ("email_tfidf", TfidfVectorizer(max_features=1000, ngram_range=(1, 2)), "email_text"),
        ],
        remainder="drop",
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", make_classifier(model_type, y)),
    ])


def get_feature_names(model: Pipeline) -> list[str]:
    try:
        names = model.named_steps["preprocessor"].get_feature_names_out()
        return [name.replace("url_features__", "").replace("email_tfidf__", "email:") for name in names]
    except Exception:
        return []


def get_feature_importance(model: Pipeline) -> list[tuple[str, float]]:
    classifier = model.named_steps["model"]
    feature_names = get_feature_names(model)
    if not feature_names:
        return []

    if hasattr(classifier, "feature_importances_"):
        scores = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        scores = np.abs(classifier.coef_[0])
    else:
        return []

    ranked = sorted(zip(feature_names, scores), key=lambda item: abs(float(item[1])), reverse=True)
    return [(name, float(score)) for name, score in ranked[:10]]


def train(data_path: str, model_out: str, model_type: str) -> None:
    model_type = normalize_model_type(model_type)
    print(f"Training model type: {model_type}")

    df = load_dataset(data_path)
    X = build_model_input(df)
    y = df["label"]
    numeric_columns = [column for column in X.columns if column != "email_text"]

    X_train, X_test, y_train, y_test = split_dataset(X, y)

    model = make_pipeline(model_type, numeric_columns, y_train)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["benign", "phishing"], zero_division=0))

    top_features = get_feature_importance(model)
    if top_features:
        print("Top 10 important features:")
        for rank, (feature, score) in enumerate(top_features, start=1):
            print(f"{rank}. {feature}: {score:.6f}")

    artifact = {
        "model": model,
        "numeric_columns": numeric_columns,
        "input_columns": list(X.columns),
        "feature_names": get_feature_names(model),
        "model_type": model_type,
        "training_data": data_path,
        "training_date": datetime.now().isoformat(timespec="seconds"),
        "supports_email_text": bool(df[["subject", "body"]].notna().any().any()) if {"subject", "body"}.issubset(df.columns) else False,
    }
    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_out)
    print(f"Saved model to {model_out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CyberGuard AI hybrid phishing classifier")
    parser.add_argument("--data", required=True, help="Path to CSV dataset with url,label or url,subject,body,label columns")
    parser.add_argument("--model-out", default="models/cyberguard_model.joblib")
    parser.add_argument(
        "--model-type",
        default="logreg",
        choices=["logreg", "logistic_regression", "rf", "random_forest", "xgboost"],
    )
    args = parser.parse_args()
    train(args.data, args.model_out, args.model_type)


if __name__ == "__main__":
    main()
