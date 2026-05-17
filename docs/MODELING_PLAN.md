# Modeling Plan

## Baseline

Mulai dari model sederhana:

1. Logistic Regression
2. Random Forest
3. XGBoost

## Pipeline

1. Load dataset.
2. Ekstraksi fitur URL.
3. Split data train-test dengan stratifikasi.
4. Training baseline model.
5. Evaluasi model.
6. Pilih model terbaik berdasarkan recall, F1-score, dan ROC-AUC.
7. Simpan model dengan Joblib.

## Metrik Utama

Untuk deteksi phishing, metrik paling penting adalah:

- Recall kelas phishing.
- F1-score kelas phishing.
- ROC-AUC.

False negative harus ditekan karena URL phishing yang diprediksi aman lebih berbahaya daripada URL aman yang salah ditandai mencurigakan.

## Eksperimen

### Eksperimen 1: Logistic Regression

Tujuan: baseline cepat dan mudah dijelaskan.

### Eksperimen 2: Random Forest

Tujuan: menangkap pola non-linear dan melihat feature importance.

### Eksperimen 3: XGBoost

Tujuan: meningkatkan performa model dengan gradient boosting.

## Output Training

Simpan artefak berikut:

- `models/cyberguard_model.joblib`
- `reports/classification_report.txt`
- `reports/confusion_matrix.png`
- `reports/feature_importance.png`

## Model Card Singkat

Tuliskan:

- Dataset yang digunakan.
- Jumlah data.
- Rasio kelas.
- Model terbaik.
- Metrik evaluasi.
- Keterbatasan.
- Penggunaan yang tidak diperbolehkan.
