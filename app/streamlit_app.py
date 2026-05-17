from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.predict import predict_url

DEFAULT_MODEL_PATH = "models/cyberguard_model.joblib"

st.set_page_config(page_title="CyberGuard AI", page_icon="🛡️", layout="centered")

st.title("🛡️ CyberGuard AI")
st.caption("Prediksi URL phishing/malicious berbasis machine learning defensif")

st.warning(
    "Aplikasi ini tidak membuka URL yang dimasukkan. Prediksi hanya berdasarkan struktur teks URL. "
    "Gunakan sebagai alat bantu edukatif, bukan jaminan keamanan final."
)

model_path = st.text_input("Path model", value=DEFAULT_MODEL_PATH)
url = st.text_input("Masukkan URL", placeholder="https://example.com")

if st.button("Predict", type="primary"):
    if not url.strip():
        st.error("URL tidak boleh kosong.")
    elif not Path(model_path).exists():
        st.error(f"Model belum ditemukan di {model_path}. Train model terlebih dahulu.")
    else:
        result = predict_url(url, model_path)
        probability = result["phishing_probability"]

        st.subheader("Hasil Prediksi")
        st.metric("Label", result["label"])
        st.metric("Probabilitas phishing", f"{probability:.2%}")
        st.metric("Risk level", result["risk_level"])

        if result["risk_level"] == "High":
            st.error("Risiko tinggi. Hindari membuka URL ini kecuali sudah diverifikasi.")
        elif result["risk_level"] == "Medium":
            st.warning("Risiko sedang. Periksa domain, ejaan, dan sumber URL.")
        else:
            st.success("Risiko rendah menurut model. Tetap berhati-hati.")

        st.subheader("Fitur URL")
        features_df = pd.DataFrame([result["features"]]).T.reset_index()
        features_df.columns = ["feature", "value"]
        st.dataframe(features_df, use_container_width=True)
