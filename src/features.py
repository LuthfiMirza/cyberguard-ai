from __future__ import annotations

import re
from typing import Iterable, Optional
from urllib.parse import ParseResult, urlparse

import pandas as pd

SUSPICIOUS_KEYWORDS = [
    "login",
    "verify",
    "secure",
    "account",
    "update",
    "banking",
    "password",
    "confirm",
    "wallet",
    "payment",
]

SUSPICIOUS_TLDS = {"xyz", "top", "click", "work", "country", "stream", "gq", "tk", "ml", "cf"}
IPV4_PATTERN = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def _safe_parse(url: str):
    raw_url = str(url or "").strip()
    if not raw_url:
        return raw_url, urlparse("")
    candidate = raw_url if "://" in raw_url else f"http://{raw_url}"
    try:
        return raw_url, urlparse(candidate)
    except ValueError:
        return raw_url, ParseResult(scheme="", netloc="", path=raw_url, params="", query="", fragment="")


def _hostname_parts(hostname: str) -> list[str]:
    return [part for part in hostname.split(".") if part]


def extract_url_features(url: str) -> dict[str, float | int]:
    """Extract safe lexical URL features without opening the URL."""
    raw_url, parsed = _safe_parse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    lowered = raw_url.lower()
    parts = _hostname_parts(hostname)
    tld = parts[-1].lower() if parts else ""
    subdomain_count = max(len(parts) - 2, 0)
    suspicious_keyword_count = sum(lowered.count(keyword) for keyword in SUSPICIOUS_KEYWORDS)
    count_digits = sum(ch.isdigit() for ch in raw_url)
    count_letters = sum(ch.isalpha() for ch in raw_url)
    url_length = len(raw_url)

    features = {
        "url_length": url_length,
        "domain_length": len(hostname),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "count_dots": raw_url.count("."),
        "count_hyphens": raw_url.count("-"),
        "count_at": raw_url.count("@"),
        "count_question": raw_url.count("?"),
        "count_equal": raw_url.count("="),
        "count_percent": raw_url.count("%"),
        "count_slash": raw_url.count("/"),
        "count_digits": count_digits,
        "count_letters": count_letters,
        "digit_ratio": count_digits / url_length if url_length else 0.0,
        "has_https": int(parsed.scheme == "https"),
        "has_ip_address": int(bool(IPV4_PATTERN.match(hostname))),
        "subdomain_count": subdomain_count,
        "num_subdomains": subdomain_count,
        "suspicious_keyword_count": suspicious_keyword_count,
        "has_suspicious_words": int(suspicious_keyword_count > 0),
        "suspicious_tld_flag": int(tld in SUSPICIOUS_TLDS),
    }
    return features


def build_feature_dataframe(urls: Iterable[str]) -> pd.DataFrame:
    """Convert URLs into a tabular numerical feature matrix."""
    return pd.DataFrame([extract_url_features(url) for url in urls])


def build_email_text(subjects: Optional[Iterable[str]], bodies: Optional[Iterable[str]]) -> pd.Series:
    subject_series = pd.Series(subjects if subjects is not None else [], dtype="string").fillna("")
    body_series = pd.Series(bodies if bodies is not None else [], dtype="string").fillna("")
    return (subject_series + " " + body_series).str.strip()


def build_model_input(df: pd.DataFrame) -> pd.DataFrame:
    """Build model input from URL-only or URL + email datasets."""
    features = build_feature_dataframe(df["url"])
    if {"subject", "body"}.issubset(df.columns):
        features["email_text"] = build_email_text(df["subject"], df["body"])
    else:
        features["email_text"] = "no_email_text"
    return features
