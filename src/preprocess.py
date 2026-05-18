from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

LABEL_MAP = {
    "good": 0,
    "bad": 1,
    "0": 0,
    "1": 1,
    "legitimate": 0,
    "benign": 0,
    "phishing": 1,
    "malicious": 1,
}


def normalize_label(value) -> int:
    key = str(value).strip().lower()
    if key not in LABEL_MAP:
        raise ValueError(f"Unsupported label value: {value!r}")
    return LABEL_MAP[key]


def preprocess(input_path: str, output_path: str) -> pd.DataFrame:
    raw_df = pd.read_csv(input_path)
    raw_rows = len(raw_df)

    required = {"URL", "Label"}
    missing = required - set(raw_df.columns)
    if missing:
        raise ValueError(f"Input must contain columns {sorted(required)}. Missing: {sorted(missing)}")

    df = raw_df.rename(columns={"URL": "url", "Label": "label"})[["url", "label"]].copy()
    df = df.dropna(subset=["url", "label"])
    df["url"] = df["url"].astype(str).str.strip()
    df = df[df["url"] != ""]
    df["label"] = df["label"].apply(normalize_label)
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)

    counts = df["label"].value_counts().to_dict()
    legitimate_count = int(counts.get(0, 0))
    phishing_count = int(counts.get(1, 0))
    total = len(df)
    legitimate_ratio = legitimate_count / total * 100 if total else 0.0
    phishing_ratio = phishing_count / total * 100 if total else 0.0

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Raw rows      : {raw_rows:,}")
    print(f"After cleaning: {total:,}")
    print(f"Legitimate (0): {legitimate_count:,} ({legitimate_ratio:.1f}%)")
    print(f"Phishing   (1): {phishing_count:,} ({phishing_ratio:.1f}%)")
    print(f"Class ratio   : {legitimate_ratio:.1f}% legitimate / {phishing_ratio:.1f}% phishing")
    print(f"Saved to {output_path}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess Kaggle phishing URL dataset")
    parser.add_argument("--input", required=True, help="Raw CSV path with URL,Label columns")
    parser.add_argument("--output", required=True, help="Output CSV path with url,label columns")
    args = parser.parse_args()
    preprocess(args.input, args.output)


if __name__ == "__main__":
    main()
