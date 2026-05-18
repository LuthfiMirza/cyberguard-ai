# Dataset Guide

## Dataset yang Disarankan

Cari dataset publik dengan kata kunci:

- `phishing url dataset`
- `malicious url dataset`
- `phishing website dataset`
- `url classification dataset`

Sumber umum:

- Kaggle
- UCI Machine Learning Repository
- PhishTank public data
- OpenPhish public feeds jika tersedia untuk edukasi

## Format Dataset Minimal

Dataset paling sederhana cukup memiliki dua kolom:

```csv
url,label
https://example.com,0
http://login-security-update-example.com,1
```

Keterangan:

- `url`: URL mentah.
- `label`: target klasifikasi.
  - `0`: benign / legitimate
  - `1`: phishing / malicious

## Format Dataset Alternatif

Beberapa dataset mungkin menggunakan label teks:

```csv
url,type
https://example.com,benign
http://fake-login.example,phishing
```

Mapping yang disarankan:

```python
{"benign": 0, "legitimate": 0, "safe": 0, "phishing": 1, "malicious": 1}
```

## Data Cleaning

Lakukan langkah berikut:

1. Hapus data duplikat.
2. Hapus URL kosong.
3. Normalisasi label menjadi `0` dan `1`.
4. Pastikan tidak ada kebocoran data seperti kolom `result`, `status`, atau `source` yang terlalu dekat dengan target.
5. Split data dengan stratifikasi label.

## Risiko Dataset

Dataset phishing sering imbalance. Jumlah URL aman dan phishing bisa tidak seimbang. Karena itu, jangan hanya mengandalkan accuracy.

Gunakan:

- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrix

## Target Dataset Awal

Untuk versi pertama, gunakan minimal:

- 5.000 URL benign
- 5.000 URL phishing/malicious

Kalau dataset kecil, tetap bisa dipakai untuk demo, tetapi jelaskan keterbatasannya di laporan.

## Dataset Nyata (Kaggle)

CyberGuard AI dapat dilatih ulang dengan dataset Kaggle **Phishing Site URLs**.

Download dataset:

```bash
kaggle datasets download taruntiwarihp/phishing-site-urls -p data/raw
unzip data/raw/phishing-site-urls.zip -d data/raw/phishing-site-urls
```

Atau jika ingin langsung unzip via Kaggle CLI:

```bash
kaggle datasets download taruntiwarihp/phishing-site-urls -p data/raw --unzip
```

Raw file yang digunakan:

```text
data/raw/phishing-site-urls/phishing_site_urls.csv
```

Format raw dataset:

```csv
URL,Label
example.com,good
suspicious-login.example,bad
```

Mapping label:

- `good` → `0` legitimate
- `bad` → `1` phishing

Jalankan preprocessing ke format pipeline CyberGuard AI:

```bash
python3 -m src.preprocess \
  --input data/raw/phishing-site-urls/phishing_site_urls.csv \
  --output data/processed/kaggle_phishing_urls.csv
```

Output processed tidak perlu di-commit ke git karena ukurannya besar dan dapat dibuat ulang dari raw dataset.
