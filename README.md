# CyberGuard AI

**CyberGuard AI** adalah sistem machine learning defensif untuk membantu mengklasifikasikan URL dan email yang berisiko phishing. Sistem menggunakan fitur struktural dari URL serta fitur NLP dari teks email seperti subject dan body.

> Project ini tidak melakukan crawling, scraping, eksploitasi, active scanning, atau request ke URL target. Fokusnya adalah edukasi, defensive security, dan portofolio machine learning.

## Problem Statement

Bagaimana membangun model machine learning yang dapat membantu mengklasifikasikan pesan atau URL sebagai legitimate atau phishing berdasarkan fitur struktural URL dan pola bahasa pada email?

Target klasifikasi:

- `0`: benign / legitimate
- `1`: phishing / suspicious

## Key Features

- URL structural feature extraction
- Email text classification dengan TF-IDF
- Hybrid ML pipeline untuk URL-only atau URL + email
- Risk score dan risk level
- Streamlit dashboard
- Defensive-only security scope
- Evaluation report dan confusion matrix

## Dataset Format

CyberGuard AI mendukung dua format dataset.

URL-only:

```csv
url,label
https://example.com,0
http://secure-login-example.net/verify,1
```

URL + email:

```csv
url,subject,body,label
https://example.com,Your order receipt,Thank you for your purchase,0
http://verify-account-example.net,Account suspended,Verify your account immediately,1
```

Sample dataset tersedia di:

- `data/sample_phishing_urls.csv`
- `data/sample_phishing_emails.csv`

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run Tests

```bash
python3 -m pytest -q
```

## Training

Train dengan sample URL + email:

```bash
python3 -m src.train --data data/sample_phishing_emails.csv --model-out models/cyberguard_model.joblib
```

Train dengan dataset URL-only:

```bash
python3 -m src.train --data data/sample_phishing_urls.csv --model-out models/cyberguard_model.joblib
```

Model default menggunakan `LogisticRegression` dengan gabungan fitur numerik URL dan TF-IDF email. `RandomForest` tersedia lewat `--model-type random_forest`.

## Evaluation

```bash
python3 -m src.evaluate --data data/sample_phishing_emails.csv --model models/cyberguard_model.joblib
```

Output evaluasi:

- `reports/evaluation_report.txt`
- `reports/confusion_matrix.png`

## Streamlit Dashboard

```bash
streamlit run app/streamlit_app.py
```

Jika command `streamlit` belum ada di PATH, gunakan:

```bash
python3 -m streamlit run app/streamlit_app.py
```

Dashboard menerima input:

- URL
- email subject (opsional)
- email body (opsional)

## Example Prediction Input

```text
URL: http://secure-login-example.net/verify-account
Subject: Account suspended
Body: Verify your account immediately to avoid access restriction.
```

Contoh output:

```text
predicted_label: phishing/malicious
risk_score: 0.87
risk_level: high
```

Nilai tersebut adalah skor bantuan klasifikasi, bukan verdict keamanan final.

## Repository Structure

```text
cyberguard-ai/
├── app/                  # Streamlit dashboard
├── data/                 # Sample datasets
├── docs/                 # Project documentation
├── models/               # Generated model artifacts
├── notebooks/            # Exploration notebook
├── prompts/              # Codex prompts
├── reports/              # Generated evaluation reports
├── src/                  # ML pipeline source code
├── tests/                # Unit tests
├── requirements.txt
└── README.md
```

## Dependencies Note

Core MVP menggunakan `pandas`, `scikit-learn`, `matplotlib`, `seaborn`, `joblib`, dan `streamlit`. Dependency seperti `xgboost` dan `shap` bersifat opsional untuk eksperimen lanjutan, bukan requirement utama pipeline hybrid saat ini.

## Security Scope

CyberGuard AI hanya untuk defensive security dan edukasi. Project ini tidak boleh digunakan untuk phishing, impersonation, credential theft, eksploitasi, atau pengujian aktif terhadap target tanpa izin. Domain age, WHOIS, dan reputation API dapat ditambahkan sebagai future work menggunakan sumber threat intelligence tepercaya.
