from __future__ import annotations

import argparse
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.data_loader import load_dataset
from src.features import build_feature_dataframe


def make_model(model_type: str):
    if model_type == "logistic_regression":
        return Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ])
    if model_type == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1,
        )
    if model_type == "xgboost":
        from xgboost import XGBClassifier

        return XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
        )
    raise ValueError(f"Unsupported model type: {model_type}")


def train(data_path: str, model_out: str, model_type: str) -> None:
    df = load_dataset(data_path)
    X = build_feature_dataframe(df["url"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = make_model(model_type)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["benign", "phishing"]))

    artifact = {
        "model": model,
        "feature_columns": list(X.columns),
        "model_type": model_type,
    }
    Path(model_out).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_out)
    print(f"Saved model to {model_out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CyberGuard AI phishing URL classifier")
    parser.add_argument("--data", required=True, help="Path to CSV dataset with url,label columns")
    parser.add_argument("--model-out", default="models/cyberguard_model.joblib")
    parser.add_argument(
        "--model-type",
        default="random_forest",
        choices=["logistic_regression", "random_forest", "xgboost"],
    )
    args = parser.parse_args()
    train(args.data, args.model_out, args.model_type)


if __name__ == "__main__":
    main()
