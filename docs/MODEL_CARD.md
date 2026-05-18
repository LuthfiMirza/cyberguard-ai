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

- Total features: 22
- URL structural features: URL length, domain length, hostname length, path length, dot count, hyphen count, `@`, `?`, `=`, `%`, slash count, digit count, letter count, digit ratio, HTTPS flag, IP address flag, subdomain count, suspicious keyword count, suspicious TLD flag
- NLP features: TF-IDF on email subject + body when available. This Kaggle training run is URL-only, so email text is not used as a signal.

## Top Features

Top features from the trained XGBoost model:

1. `suspicious_keyword_count`
2. `has_ip_address`
3. `suspicious_tld_flag`
4. `count_hyphens`
5. `count_digits`

## Performance (Evaluation Set)

| Metric | Value |
|---|---:|
| Accuracy | 0.8780 |
| Precision (phishing) | 0.6886 |
| Recall (phishing) | 0.8371 |
| F1-score (phishing) | 0.7557 |
| ROC-AUC | 0.9432 |

Confusion matrix:

```text
[[349634  43263]
 [ 18614  95681]]
```

## Limitations

- Trained on a public URL-only dataset; email NLP behavior should be evaluated separately with a real email dataset.
- Does not perform live domain reputation lookup.
- Does not crawl, scrape, or request the target URL.
- Adversarial URLs crafted to evade structural features may bypass detection.
- False positives are possible, especially because the model prioritizes phishing recall.

## Ethical Considerations

- Not to be used for offensive purposes.
- False negatives (missed phishing) remain a risk — always combine with human judgment.
- Use only on data you are authorized to analyze.
