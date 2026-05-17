# CyberGuard AI

**CyberGuard AI** adalah proyek machine learning untuk memprediksi apakah sebuah URL berpotensi **phishing/malicious** atau **benign/aman** berdasarkan fitur URL dan metadata sederhana.

> Fokus proyek ini adalah deteksi defensif, edukasi keamanan, dan portofolio machine learning. Proyek ini tidak dibuat untuk menyerang sistem, mencuri kredensial, atau melakukan aktivitas ilegal.

## 1. Tujuan Proyek

Membangun sistem prediksi phishing URL yang dapat:

- menerima input URL,
- mengekstrak fitur dari URL,
- memprediksi apakah URL aman atau mencurigakan,
- menampilkan probabilitas risiko,
- menjelaskan faktor yang memengaruhi prediksi,
- menyediakan demo sederhana melalui Streamlit.

## 2. Problem Statement

Phishing adalah salah satu ancaman siber paling umum. Banyak serangan dimulai dari URL palsu yang meniru situs resmi. Proyek ini bertujuan membuat model ML yang dapat membantu pengguna mengenali URL mencurigakan lebih awal.

Target klasifikasi:

- `0`: Benign / Legitimate
- `1`: Phishing / Malicious

## 3. Tech Stack

- Python 3.10+
- Pandas
- NumPy
- Scikit-learn
- XGBoost atau LightGBM opsional
- Matplotlib
- Seaborn
- SHAP opsional
- Streamlit
- Joblib

## 4. Struktur Folder

```text
cyberguard-ai/
├── app/
│   └── streamlit_app.py
├── data/
│   └── .gitkeep
├── docs/
│   ├── DATASET_GUIDE.md
│   ├── FEATURE_ENGINEERING.md
│   ├── MODELING_PLAN.md
│   ├── PROJECT_SPEC.md
│   └── SECURITY_SCOPE.md
├── models/
│   └── .gitkeep
├── notebooks/
│   └── 01_exploration.ipynb
├── prompts/
│   ├── CODEX_MASTER_PROMPT.md
│   ├── CODEX_STEP_BY_STEP_PROMPTS.md
│   └── COMMIT_PROMPTS.md
├── reports/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── evaluate.py
│   ├── features.py
│   ├── predict.py
│   └── train.py
├── tests/
│   ├── __init__.py
│   └── test_features.py
├── .gitignore
├── requirements.txt
└── README.md
```

## 5. Setup Awal

### Clone atau buat folder project

```bash
mkdir cyberguard-ai
cd cyberguard-ai
```

### Buat virtual environment

```bash
python -m venv .venv
```

Aktifkan environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Dataset

Letakkan dataset di folder `data/`.

Format minimal dataset:

```csv
url,label
https://example.com,0
http://login-bank-security-example.com,1
```

Kolom wajib:

- `url`: alamat URL
- `label`: target klasifikasi, `0` untuk aman dan `1` untuk phishing/malicious

Baca detailnya di [`docs/DATASET_GUIDE.md`](docs/DATASET_GUIDE.md).

## 7. Pipeline ML

Tahapan utama:

1. Load dataset
2. Bersihkan data
3. Ekstraksi fitur URL
4. Split train-test
5. Train model baseline
6. Evaluasi model
7. Simpan model
8. Buat demo Streamlit

## 8. Cara Training Model

```bash
python -m src.train --data data/phishing_urls.csv --model-out models/cyberguard_model.joblib
```

## 9. Cara Evaluasi Model

```bash
python -m src.evaluate --data data/phishing_urls.csv --model models/cyberguard_model.joblib
```

## 10. Cara Menjalankan Demo

```bash
streamlit run app/streamlit_app.py
```

## 11. Contoh Input Demo

```text
https://www.google.com
http://secure-login-paypal-verification.example.ru/login
https://github.com/openai
```

## 12. Metrik Evaluasi

Gunakan metrik berikut:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion Matrix

Untuk kasus phishing, **recall untuk kelas phishing** sangat penting karena false negative berbahaya: URL phishing tetapi diprediksi aman.

## 13. Roadmap

- [ ] Baseline Logistic Regression
- [ ] Random Forest
- [ ] XGBoost
- [ ] Feature importance
- [ ] SHAP explanation
- [ ] Streamlit dashboard
- [ ] Batch prediction CSV
- [ ] Model card

## 14. Disclaimer

CyberGuard AI hanya alat bantu pembelajaran dan deteksi awal. Hasil prediksi tidak boleh dijadikan satu-satunya dasar keputusan keamanan. Untuk penggunaan nyata, kombinasikan dengan threat intelligence, sandboxing, reputasi domain, dan validasi pakar keamanan.
