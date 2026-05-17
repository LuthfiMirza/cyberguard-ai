# Codex Step-by-Step Prompts

Gunakan prompt ini satu per satu kalau ingin proses lebih terkontrol.

## Prompt 1: Buat Struktur Repo

```text
Buat struktur repo Python untuk proyek CyberGuard AI. Proyek ini adalah sistem ML defensif untuk klasifikasi URL phishing. Buat folder app, data, docs, models, notebooks, prompts, reports, src, dan tests. Tambahkan README.md, requirements.txt, .gitignore, dan file .gitkeep pada folder kosong. Jangan implementasi model dulu.
```

## Prompt 2: Implementasi Feature Engineering

```text
Implementasikan `src/features.py` untuk ekstraksi fitur lexical dari URL tanpa membuka URL atau mengirim request jaringan. Buat fungsi `extract_url_features(url: str) -> dict` dan `build_feature_dataframe(urls)`. Fitur minimal: panjang URL, panjang hostname, panjang path, jumlah titik, hyphen, @, ?, =, slash, angka, huruf, rasio angka, HTTPS, IP address, suspicious words, dan jumlah subdomain. Tambahkan type hints dan handling URL kosong.
```

## Prompt 3: Data Loader

```text
Implementasikan `src/data_loader.py`. Buat fungsi `load_dataset(path: str)` yang membaca CSV, memastikan ada kolom `url` dan `label`, menghapus missing value dan duplicate, serta mengubah label teks seperti benign/legitimate/safe menjadi 0 dan phishing/malicious menjadi 1. Berikan error message yang jelas jika format dataset salah.
```

## Prompt 4: Training Pipeline

```text
Implementasikan `src/train.py` sebagai CLI untuk training model. Terima argumen `--data`, `--model-out`, dan `--model-type`. Pilihan model: logistic_regression, random_forest, xgboost. Gunakan train_test_split dengan stratify. Ekstrak fitur URL, train model, tampilkan classification report, dan simpan model dengan joblib. Pastikan model yang disimpan bisa langsung dipakai untuk prediksi URL baru.
```

## Prompt 5: Evaluasi

```text
Implementasikan `src/evaluate.py` untuk evaluasi model yang sudah dilatih. Load dataset dan model, hitung accuracy, precision, recall, f1, ROC-AUC, dan confusion matrix. Simpan classification report ke `reports/classification_report.txt`. Fokuskan interpretasi pada recall kelas phishing.
```

## Prompt 6: Prediction Helper

```text
Implementasikan `src/predict.py`. Buat fungsi `predict_url(url: str, model_path: str)` yang mengekstrak fitur URL, load model joblib, menghasilkan label prediksi, probabilitas phishing, dan risk level: Low jika < 0.35, Medium jika 0.35 sampai < 0.70, High jika >= 0.70.
```

## Prompt 7: Streamlit App

```text
Buat `app/streamlit_app.py` untuk demo CyberGuard AI. UI harus memiliki input URL, tombol Predict, output label, probabilitas phishing, risk level, dan tabel fitur URL. Jangan membuka URL input. Tambahkan disclaimer bahwa hasil prediksi adalah alat bantu edukatif, bukan jaminan keamanan.
```

## Prompt 8: Unit Test

```text
Buat unit test di `tests/test_features.py` untuk memastikan feature extraction berjalan. Test URL HTTPS normal, URL dengan IP address, URL kosong, dan URL yang mengandung suspicious words seperti login atau verify.
```

## Prompt 9: Rapikan README

```text
Perbarui README.md agar lengkap: deskripsi proyek, tujuan, struktur folder, setup virtual environment, install dependencies, format dataset, cara training, cara evaluasi, cara menjalankan Streamlit, metrik evaluasi, roadmap, dan disclaimer keamanan.
```

## Prompt 10: Final Review

```text
Review seluruh repo CyberGuard AI. Pastikan semua import benar, command di README cocok dengan kode, tidak ada fungsi yang mengakses internet, semua path masuk akal, dan proyek bisa dijalankan dari awal oleh pemula. Jika ada bug, perbaiki.
```
