# Codex Master Prompt

Gunakan prompt ini di Codex untuk membangun proyek dari awal.

```text
Kamu adalah senior machine learning engineer dan cybersecurity-aware developer. Bantu saya membangun proyek bernama CyberGuard AI, yaitu sistem machine learning defensif untuk memprediksi apakah sebuah URL termasuk benign atau phishing/malicious.

Tujuan proyek:
- Membuat pipeline ML end-to-end dari dataset CSV.
- Dataset minimal memiliki kolom `url` dan `label`.
- Label: 0 = benign, 1 = phishing/malicious.
- Ekstraksi fitur dilakukan dari teks URL saja.
- Jangan melakukan request/crawling ke URL input.
- Fokus pada penggunaan aman, edukatif, dan defensif.

Struktur repo yang harus dibuat:

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

Implementasi yang saya butuhkan:

1. `src/features.py`
   - Buat fungsi `extract_url_features(url: str) -> dict`.
   - Fitur minimal:
     - url_length
     - hostname_length
     - path_length
     - count_dots
     - count_hyphens
     - count_at
     - count_question
     - count_equal
     - count_slash
     - count_digits
     - count_letters
     - digit_ratio
     - has_https
     - has_ip_address
     - has_suspicious_words
     - num_subdomains
   - Buat fungsi `build_feature_dataframe(urls)` yang mengubah list/Series URL menjadi DataFrame fitur.

2. `src/data_loader.py`
   - Load CSV.
   - Validasi kolom `url` dan `label`.
   - Drop missing value dan duplicate.
   - Normalisasi label jika masih berbentuk teks.

3. `src/train.py`
   - CLI argument:
     - `--data`
     - `--model-out`
     - `--model-type`, default random_forest, pilihan logistic_regression/random_forest/xgboost.
   - Split train-test stratified.
   - Train model.
   - Print classification report.
   - Simpan model pipeline ke Joblib.

4. `src/evaluate.py`
   - Load model.
   - Load dataset.
   - Evaluasi dengan accuracy, precision, recall, f1, ROC-AUC, confusion matrix.
   - Simpan classification report ke folder reports.

5. `src/predict.py`
   - Fungsi `predict_url(url: str, model_path: str)`.
   - Return label, probability, dan risk level: Low/Medium/High.

6. `app/streamlit_app.py`
   - UI sederhana.
   - Input URL.
   - Tombol Predict.
   - Tampilkan hasil prediksi, probabilitas, risk level, dan beberapa fitur URL.
   - Tambahkan disclaimer keamanan.

7. `tests/test_features.py`
   - Unit test sederhana untuk feature extraction.

8. README
   - Jelaskan setup, dataset, training, evaluasi, menjalankan Streamlit, dan disclaimer.

Standar kualitas:
- Kode harus rapi dan mudah dibaca.
- Gunakan type hints jika memungkinkan.
- Tambahkan error handling yang wajar.
- Jangan hardcode path selain default yang masuk akal.
- Jangan akses internet dari kode.
- Jangan membuat fungsi ofensif.

Mulai dengan membuat semua file dan implementasi versi MVP yang bisa dijalankan.
```
