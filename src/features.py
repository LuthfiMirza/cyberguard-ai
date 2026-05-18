from __future__ import annotations

import re
from typing import Iterable, Optional
from urllib.parse import ParseResult, urlparse

import pandas as pd

from src.brands import TOP_BRANDS

try:
    import Levenshtein
    import tldextract
except ImportError:
    Levenshtein = None
    tldextract = None

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

def extract_sld(url: str) -> str:
    raw_url, parsed = _safe_parse(url)
    hostname = parsed.hostname or ""
    target = raw_url if "://" in raw_url else f"http://{raw_url}"
    if tldextract is not None:
        try:
            extracted = tldextract.extract(target)
            return (extracted.domain or "").lower()
        except Exception:
            pass

    parts = _hostname_parts(hostname)
    if len(parts) >= 2 and parts[-2] in {"co", "ac", "go", "or", "web", "net"} and len(parts[-1]) == 2:
        return parts[-3].lower() if len(parts) >= 3 else ""
    return parts[-2].lower() if len(parts) >= 2 else (parts[0].lower() if parts else "")

def get_typosquatting_features(url: str) -> dict[str, float | int]:
    default_features = {
        "min_brand_levenshtein": 0,
        "is_typosquatting": 0,
        "exact_brand_match": 0,
        "brand_impersonation_score": 0.0,
    }
    if Levenshtein is None:
        return default_features

    domain = extract_sld(url)
    if not domain:
        return default_features

    distances = [Levenshtein.distance(domain, brand) for brand in TOP_BRANDS]
    min_distance = min(distances) if distances else 0
    exact_brand_match = int(min_distance == 0 and domain in TOP_BRANDS)
    is_typosquatting = int(1 <= min_distance <= 2)
    return {
        "min_brand_levenshtein": int(min_distance),
        "is_typosquatting": is_typosquatting,
        "exact_brand_match": exact_brand_match,
        "brand_impersonation_score": 1.0 / (min_distance + 1),
    }


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
    features.update(get_typosquatting_features(url))
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
