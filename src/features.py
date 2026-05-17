from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable
from urllib.parse import urlparse

import pandas as pd

from src.config import SUSPICIOUS_WORDS

IPV4_PATTERN = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def _safe_parse(url: str):
    raw_url = str(url or "").strip()
    if not raw_url:
        return raw_url, urlparse("")
    candidate = raw_url if "://" in raw_url else f"http://{raw_url}"
    return raw_url, urlparse(candidate)


def _entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return float(-sum((count / total) * math.log2(count / total) for count in counts.values()))


def extract_url_features(url: str) -> dict[str, float | int]:
    """Extract safe lexical features from a URL without opening it."""
    raw_url, parsed = _safe_parse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    lowered = raw_url.lower()

    count_digits = sum(ch.isdigit() for ch in raw_url)
    count_letters = sum(ch.isalpha() for ch in raw_url)
    url_length = len(raw_url)

    hostname_parts = [part for part in hostname.split(".") if part]
    num_subdomains = max(len(hostname_parts) - 2, 0)

    return {
        "url_length": url_length,
        "hostname_length": len(hostname),
        "path_length": len(path),
        "count_dots": raw_url.count("."),
        "count_hyphens": raw_url.count("-"),
        "count_at": raw_url.count("@"),
        "count_question": raw_url.count("?"),
        "count_equal": raw_url.count("="),
        "count_slash": raw_url.count("/"),
        "count_digits": count_digits,
        "count_letters": count_letters,
        "digit_ratio": count_digits / url_length if url_length else 0.0,
        "has_https": int(parsed.scheme == "https"),
        "has_ip_address": int(bool(IPV4_PATTERN.match(hostname))),
        "has_suspicious_words": int(any(word in lowered for word in SUSPICIOUS_WORDS)),
        "num_subdomains": num_subdomains,
        "url_entropy": _entropy(raw_url),
    }


def build_feature_dataframe(urls: Iterable[str]) -> pd.DataFrame:
    """Convert URLs into a tabular feature matrix."""
    return pd.DataFrame([extract_url_features(url) for url in urls])
