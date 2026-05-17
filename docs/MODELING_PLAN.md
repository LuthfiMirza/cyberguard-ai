# Modeling Plan

## Baseline MVP

- Preprocessing numerik URL dengan `StandardScaler`.
- Preprocessing email text dengan `TfidfVectorizer`.
- Penggabungan fitur menggunakan `ColumnTransformer`.
- Classifier default: `LogisticRegression`.
- Classifier alternatif ringan: `RandomForestClassifier`.

## Evaluation

Metrik utama:

- Accuracy
- Precision phishing
- Recall phishing
- F1 phishing
- ROC-AUC jika tersedia
- Confusion matrix
- Classification report

## Dataset Modes

- URL-only: `url,label`.
- Hybrid email: `url,subject,body,label`.

## Future Work

- Domain age dan reputation API sebagai fitur opsional dari threat intelligence tepercaya.
- Explainability dengan feature importance atau SHAP.
- Batch prediction CSV.
