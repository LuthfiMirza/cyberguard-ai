from __future__ import annotations

import pandas as pd

LABEL_MAP = {
    "0": 0,
    "1": 1,
    "benign": 0,
    "legitimate": 0,
    "safe": 0,
    "good": 0,
    "phishing": 1,
    "malicious": 1,
    "bad": 1,
}


def normalize_label(value) -> int:
    key = str(value).strip().lower()
    if key not in LABEL_MAP:
        raise ValueError(f"Unsupported label value: {value!r}")
    return LABEL_MAP[key]


def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"url", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset must contain columns: {sorted(required)}. Missing: {sorted(missing)}")

    columns = ["url", "label"]
    if {"subject", "body"}.issubset(df.columns):
        columns = ["url", "subject", "body", "label"]

    df = df[columns].dropna(subset=["url", "label"]).drop_duplicates().copy()
    df["url"] = df["url"].astype(str).str.strip()
    if "subject" in df.columns:
        df["subject"] = df["subject"].fillna("").astype(str).str.strip()
    if "body" in df.columns:
        df["body"] = df["body"].fillna("").astype(str).str.strip()
    df = df[df["url"] != ""]
    df["label"] = df["label"].apply(normalize_label)
    return df.reset_index(drop=True)
