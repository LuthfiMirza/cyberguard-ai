# CyberGuard AI

Sistem deteksi phishing berbasis machine learning yang membantu mengklasifikasikan URL dan konten email sebagai legitimate atau berisiko phishing.

Proyek ini dibuat untuk tujuan **defensif**: edukasi keamanan siber dan portofolio machine learning. Tidak ada fitur ofensif, crawling, scraping, request ke URL target, atau eksploitasi sistem.

## Fitur Utama

- Deteksi phishing dari URL saja, atau kombinasi URL + subject + body email
- Ekstraksi fitur struktural URL: panjang URL/domain/path, karakter khusus, IP address, subdomain, keyword, dan TLD mencurigakan
- Analisis teks email menggunakan TF-IDF dari subject dan body
- Hybrid ML pipeline berbasis scikit-learn
- Model klasifikasi: Logistic Regression, Random Forest, dan XGBoost jika runtime tersedia
- Batch prediction dari CSV
- SHAP explanation plots untuk interpretasi model jika dependency tersedia
- Evaluasi: Accuracy, Precision, Recall, F1-score, ROC-AUC, Classification Report, dan Confusion Matrix
- Dashboard interaktif via Streamlit

## Struktur Proyek

```text
cyberguard-ai/
├── app/
│   └── streamlit_app.py        # Dashboard Streamlit
├── data/
│   ├── sample_phishing_urls.csv
│   └── sample_phishing_emails.csv
├── docs/
│   ├── DATASET_GUIDE.md
│   ├── FEATURE_ENGINEERING.md
│   ├── MODELING_PLAN.md
│   ├── PROJECT_SPEC.md
│   └── SECURITY_SCOPE.md
├── models/                     # Model tersimpan, di-ignore git
├── notebooks/
│   └── 01_exploration.ipynb
├── reports/                    # Output evaluasi, di-ignore git
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── evaluate.py
│   ├── features.py
│   ├── predict.py
│   └── train.py
├── tests/
│   └── test_features.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Buat virtual environment:

```bash
python3 -m venv .venv
```

Aktifkan virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Format Dataset

URL-only:

```csv
url,label
https://example.com,0
http://secure-login-example.net/verify,1
```

URL + email:

```csv
url,subject,body,label
https://example.com,Welcome,Hello there,0
http://verify-account-example.net,Account suspended,Verify your account immediately,1
```

Kolom `label` menggunakan format:

- `0`: benign / legitimate
- `1`: phishing / suspicious

Sample dataset tersedia di `data/sample_phishing_urls.csv` dan `data/sample_phishing_emails.csv`. Detail format ada di `docs/DATASET_GUIDE.md`.

## Cara Penggunaan

Training dengan dataset URL-only:

```bash
python3 -m src.train --data data/sample_phishing_urls.csv --model-out models/cyberguard_model.joblib
```

Training dengan dataset hybrid URL + email:

```bash
python3 -m src.train --data data/sample_phishing_emails.csv --model-out models/cyberguard_model.joblib
```

Training dengan XGBoost:

```bash
python3 -m src.train --data data/sample_phishing_emails.csv --model-out models/cyberguard_model.joblib --model-type xgboost
```

Evaluasi model:

```bash
python3 -m src.evaluate --data data/sample_phishing_emails.csv --model models/cyberguard_model.joblib
```

Prediksi satu URL:

```bash
python3 -m src.predict --url "http://secure-login-example.net/verify"
```

Prediksi URL + email:

```bash
python3 -m src.predict \
  --url "http://verify-account-example.net" \
  --subject "Account suspended" \
  --body "Verify your account immediately to restore access"
```

Batch prediction dari CSV:

```bash
python3 -m src.predict --batch data/sample_phishing_urls.csv
```

Jalankan dashboard:

```bash
streamlit run app/streamlit_app.py
```

Jika `streamlit` belum tersedia di PATH:

```bash
python3 -m streamlit run app/streamlit_app.py
```

## Contoh Input

Aman:

```text
https://www.example.com
https://docs.example.com/getting-started
```

Mencurigakan:

```text
http://secure-login-example.net/verify-account
http://192.168.1.1/banking/verify?token=abc123
```

Contoh output prediksi:

```text
predicted_label: phishing/malicious
risk_score: 0.87
risk_level: high
```

Output adalah skor bantuan klasifikasi, bukan verdict keamanan final.

## Metrik Evaluasi

| Metrik | Keterangan |
|---|---|
| Accuracy | Proporsi prediksi benar secara keseluruhan |
| Precision | Dari yang diprediksi phishing, berapa yang benar |
| Recall | Dari semua phishing nyata, berapa yang berhasil diklasifikasikan |
| F1-score | Harmonic mean precision dan recall |
| ROC-AUC | Kemampuan model membedakan dua kelas jika probabilitas tersedia |
| Confusion Matrix | Ringkasan benar/salah untuk tiap kelas |

Recall untuk kelas phishing penting karena false negative, yaitu phishing yang diklasifikasikan aman, dapat lebih berisiko daripada false positive.

## Tests

```bash
python3 -m pytest -q
```

Test mencakup ekstraksi fitur URL, deteksi keyword mencurigakan, IP address, HTTPS, input kosong, dan TLD mencurigakan.

## Roadmap

- [x] Baseline Logistic Regression
- [x] Pipeline hybrid URL + email NLP
- [x] Dashboard Streamlit
- [x] Evaluation report dan confusion matrix
- [x] Random Forest option
- [x] XGBoost option dengan fallback runtime-safe
- [x] SHAP feature explanation
- [x] Batch prediction dari CSV
- [ ] Model card
- [ ] Screenshot dashboard untuk README

## Disclaimer

CyberGuard AI adalah alat bantu pembelajaran dan deteksi awal. Hasil prediksi tidak boleh dijadikan satu-satunya dasar keputusan keamanan. Untuk penggunaan produksi, kombinasikan dengan threat intelligence feed, sandboxing, reputasi domain, dan validasi pakar keamanan.
