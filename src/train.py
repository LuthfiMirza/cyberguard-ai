from __future__ import annotations

import argparse
from pathlib import Path

import joblib
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


def split_dataset(X, y):
    try:
        return train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError as error:
        print(f"Stratified split failed, falling back to regular split: {error}")
        return train_test_split(X, y, test_size=0.2, random_state=42)


def make_classifier(model_type: str):
    if model_type == "logistic_regression":
        return LogisticRegression(max_iter=1000, class_weight="balanced")
    if model_type == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        )
    raise ValueError(f"Unsupported model type: {model_type}")


def make_pipeline(model_type: str, numeric_columns: list[str]) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("url_features", StandardScaler(), numeric_columns),
            ("email_tfidf", TfidfVectorizer(max_features=1000, ngram_range=(1, 2)), "email_text"),
        ],
        remainder="drop",
    )
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", make_classifier(model_type)),
    ])


def train(data_path: str, model_out: str, model_type: str) -> None:
    df = load_dataset(data_path)
    X = build_model_input(df)
    y = df["label"]
    numeric_columns = [column for column in X.columns if column != "email_text"]

    X_train, X_test, y_train, y_test = split_dataset(X, y)

    model = make_pipeline(model_type, numeric_columns)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["benign", "phishing"], zero_division=0))

    artifact = {
        "model": model,
        "numeric_columns": numeric_columns,
        "input_columns": list(X.columns),
        "model_type": model_type,
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
        default="logistic_regression",
        choices=["logistic_regression", "random_forest"],
    )
    args = parser.parse_args()
    train(args.data, args.model_out, args.model_type)


if __name__ == "__main__":
    main()
