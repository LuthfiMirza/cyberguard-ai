# Model Card — CyberGuard AI

## Model Details

- Model type: xgboost, with RandomForest fallback if XGBoost runtime is unavailable
- Training date: generated during the latest `src.train` run
- Framework: scikit-learn / XGBoost

## Intended Use

- Defensive phishing detection for education and portfolio purposes.
- Not for production security systems without additional validation.

## Training Data

- Dataset: `data/sample_phishing_emails.csv`
- Size: 56 rows
- Class distribution: 25 benign / 31 phishing

## Features

- Total features: generated from URL structural features plus TF-IDF vocabulary
- URL structural features: URL length, domain length, path length, special character counts, HTTPS flag, IP address flag, subdomain count, suspicious keyword count, suspicious TLD flag
- NLP features: TF-IDF on email subject + body if available

## Performance (Test Set)

| Metric | Value |
|---|---:|
| Accuracy | 1.0000 |
| Precision | 1.0000 |
| Recall (phishing) | 1.0000 |
| F1-score | 1.0000 |
| ROC-AUC | 1.0000 |

## Limitations

- Trained on small sample dataset; real-world performance may vary.
- Does not perform live domain reputation lookup.
- Does not crawl, scrape, or request the target URL.
- Adversarial URLs crafted to evade structural features may bypass detection.

## Ethical Considerations

- Not to be used for offensive purposes.
- False negatives (missed phishing) remain a risk — always combine with human judgment.
- Use only on data you are authorized to analyze.
