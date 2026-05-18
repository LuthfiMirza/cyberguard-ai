# Model Card — CyberGuard AI

## Model Details

- Model type: XGBoost
- Training date: 2026-05-18 14:38:57 Asia/Jakarta
- Framework: scikit-learn / XGBoost

## Intended Use

- Defensive phishing URL classification for education and portfolio purposes.
- Not for production security systems without additional validation.

## Training Data

- Dataset: `data/processed/kaggle_phishing_urls.csv`
- Source raw file: `data/raw/phishing-site-urls/phishing_site_urls.csv`
- Size after cleaning: 507,192 rows
- Class distribution: 392,897 legitimate / 114,295 phishing
- Label mapping: `good` → `0`, `bad` → `1`

## Features

- Total features: 26
- URL structural features: URL length, domain length, hostname length, path length, dot count, hyphen count, `@`, `?`, `=`, `%`, slash count, digit count, letter count, digit ratio, HTTPS flag, IP address flag, subdomain count, suspicious keyword count, suspicious TLD flag
- Typosquatting features (4):
  - `min_brand_levenshtein`: minimum edit distance to curated brand list
  - `is_typosquatting`: flag if edit distance is 1–2
  - `exact_brand_match`: flag if second-level domain exactly matches a known brand
  - `brand_impersonation_score`: brand similarity score from 0–1
- NLP features: TF-IDF on email subject + body when available. This Kaggle training run is URL-only, so email text is not used as a signal.

## Top Features

Top features from the trained XGBoost model:

1. `suspicious_keyword_count`
2. `brand_impersonation_score`
3. `suspicious_tld_flag`
4. `count_digits`
5. `exact_brand_match`

## Performance (Evaluation Set)

| Metric | Value |
|---|---:|
| Accuracy | 0.8874 |
| Precision (phishing) | 0.7077 |
| Recall (phishing) | 0.8525 |
| F1-score (phishing) | 0.7734 |
| ROC-AUC | 0.9512 |

Confusion matrix:

```text
[[352648  40249]
 [ 16858  97437]]
```

## Limitations

- Trained on a public URL-only dataset; email NLP behavior should be evaluated separately with a real email dataset.
- Does not perform live domain reputation lookup.
- Does not crawl, scrape, or request the target URL.
- Model now detects simple typosquatting with edit distance 1–2.
- Typosquatting with edit distance > 2 or homoglyph tricks such as `rn` vs `m` and `0` vs `o` may still bypass detection.
- Adversarial URLs crafted to evade structural features may bypass detection.
- False positives are possible, especially because the model prioritizes phishing recall.

## Ethical Considerations

- Not to be used for offensive purposes.
- False negatives (missed phishing) remain a risk — always combine with human judgment.
- Use only on data you are authorized to analyze.
