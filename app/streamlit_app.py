from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.predict import predict_url

DEFAULT_MODEL_PATH = "models/cyberguard_model.joblib"

st.set_page_config(page_title="CyberGuard AI", page_icon="🛡️", layout="centered")

st.title("🛡️ CyberGuard AI")
st.caption("Hybrid phishing classification with URL features and optional email NLP")

st.warning(
    "Aplikasi ini tidak membuka URL, tidak crawling, dan tidak melakukan request ke target. "
    "Prediksi hanya alat bantu klasifikasi edukatif, bukan verdict keamanan final."
)

model_path = st.text_input("Path model", value=DEFAULT_MODEL_PATH)
url = st.text_input("URL", placeholder="https://example.com")
subject = st.text_input("Email subject (optional)", placeholder="Account verification notice")
body = st.text_area("Email body (optional)", placeholder="Paste email text here if available")

if st.button("Predict", type="primary"):
    if not url.strip():
        st.error("URL tidak boleh kosong.")
    elif not Path(model_path).exists():
        st.error(f"Model belum ditemukan di {model_path}. Train model terlebih dahulu.")
    else:
        result = predict_url(url, model_path, subject=subject, body=body)
        risk_score = result["risk_score"]

        st.subheader("Hasil Prediksi")
        st.metric("Predicted label", result["predicted_label"])
        st.metric("Risk score", f"{risk_score:.2%}")
        st.metric("Risk level", result["risk_level"])

        if result["risk_level"] == "high":
            st.error("Risiko tinggi menurut model. Verifikasi sumber sebelum berinteraksi.")
        elif result["risk_level"] == "medium":
            st.warning("Risiko sedang. Periksa domain, ejaan, konteks email, dan sumber URL.")
        else:
            st.success("Risiko rendah menurut model. Tetap berhati-hati.")

        st.subheader("Top URL Features")
        features_df = pd.DataFrame([result["features"]]).T.reset_index()
        features_df.columns = ["feature", "value"]
        st.dataframe(features_df, use_container_width=True)
