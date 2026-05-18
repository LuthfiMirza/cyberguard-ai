from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import Optional

import joblib
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.features import extract_url_features
from src.predict import predict_batch, predict_url
from src.train import train

DEFAULT_MODEL_PATH = "models/cyberguard_model.joblib"
DEFAULT_SAMPLE_DATASET = "data/sample_phishing_emails.csv"

st.set_page_config(page_title="CyberGuard AI", page_icon="🛡️", layout="wide")


@st.cache_resource(show_spinner="Preparing demo model...")
def ensure_demo_model(model_path: str):
    model_file = Path(model_path)
    if not model_file.exists() and Path(DEFAULT_SAMPLE_DATASET).exists():
        train(DEFAULT_SAMPLE_DATASET, model_path, "logreg")
    if not model_file.exists():
        return None
    return joblib.load(model_path)


def render_badge(label: str) -> None:
    if label == "benign":
        color = "#16a34a"
        text = "SAFE"
    else:
        color = "#dc2626"
        text = "PHISHING"
    st.markdown(
        f"""
        <div style="background:{color};color:white;padding:18px;border-radius:12px;
                    text-align:center;font-size:28px;font-weight:700;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_model_info(model_path: str, artifact: Optional[dict]) -> dict[str, str | int]:
    path = Path(model_path)
    if artifact is None or not path.exists():
        return {"Tipe model": "not loaded", "Tanggal training": "n/a", "Jumlah fitur": 0}
    mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Tipe model": artifact.get("model_type", "unknown"),
        "Tanggal training": artifact.get("training_date", mtime),
        "Jumlah fitur": len(artifact.get("feature_names", [])),
    }


def top_model_features(artifact: Optional[dict], limit: int = 5) -> pd.DataFrame:
    if not artifact:
        return pd.DataFrame()
    model = artifact.get("model")
    feature_names = artifact.get("feature_names", [])
    if not model or not feature_names:
        return pd.DataFrame()
    classifier = model.named_steps.get("model")
    if hasattr(classifier, "feature_importances_"):
        scores = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        scores = abs(classifier.coef_[0])
    else:
        return pd.DataFrame()
    data = pd.DataFrame({"feature": feature_names, "importance": scores})
    return data.sort_values("importance", ascending=False).head(limit).set_index("feature")


st.title("🛡️ CyberGuard AI")
st.caption("Deteksi phishing dari pola URL dan konten email — tanpa membuka atau mengakses target.")

badge_cols = st.columns(3)
badge_texts = ["🔒 No URL Requests", "🚫 No Crawling", "📊 Pattern-Based Analysis"]
for column, badge_text in zip(badge_cols, badge_texts):
    column.markdown(
        f"""
        <div style="border:1px solid #e2e8f0;border-radius:10px;padding:10px 12px;
                    background:#f8fafc;text-align:center;font-size:0.92rem;color:#334155;">
            {badge_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption("_Hasil prediksi adalah alat bantu awal, bukan keputusan keamanan final._")

model_path = st.sidebar.text_input("Model path", value=DEFAULT_MODEL_PATH)
artifact = ensure_demo_model(model_path)
st.sidebar.subheader("ℹ️ Informasi Model")
for key, value in get_model_info(model_path, artifact).items():
    st.sidebar.write(f"**{key}:** {value}")
st.sidebar.caption("Dataset: 507.192 URL · Kaggle Phishing Site URLs")
st.sidebar.markdown("---")
st.sidebar.caption("CyberGuard AI · Proyek ML Defensif")
st.sidebar.caption("Tidak melakukan request ke URL target.")

single_tab, batch_tab = st.tabs(["🔍 Analisis URL", "📋 Analisis Batch"])

with single_tab:
    input_col, result_col = st.columns([1, 1])

    with input_col:
        st.subheader("Input")
        url = st.text_input("Masukkan URL yang ingin dianalisis", placeholder="https://contoh.com/halaman")
        with st.expander("➕ Tambahkan konten email (opsional)"):
            st.caption("Menambahkan subject dan body email meningkatkan akurasi analisis.")
            subject = st.text_input("Subject", placeholder="Account verification notice")
            body = st.text_area("Body", placeholder="Paste email text here if available")
        analyze = st.button("🔍 Analisis Sekarang", type="primary")

    with result_col:
        st.subheader("Result")
        if not analyze:
            st.info("Masukkan URL di sebelah kiri, lalu klik **Analisis Sekarang** untuk melihat hasil.")
        else:
            if not url.strip():
                st.error("URL wajib diisi.")
            elif artifact is None:
                st.error(f"Model belum ditemukan di {model_path}. Train model terlebih dahulu.")
            else:
                result = predict_url(url, model_path, subject=subject, body=body)
                risk_score = result["risk_score"]
                if result["prediction"] == 0:
                    st.success("✅ AMAN")
                    st.caption("Pola URL tidak menunjukkan tanda-tanda phishing yang signifikan.")
                else:
                    st.error("🚨 PHISHING TERDETEKSI")
                    st.caption("URL ini memiliki pola yang mirip dengan data phishing. Berhati-hatilah.")
                st.write(f"**Risk score:** {risk_score:.2%}")
                st.progress(min(max(risk_score, 0.0), 1.0))
                st.write(f"**Risk level:** {result['risk_level']}")

                features_df = pd.DataFrame([extract_url_features(url)]).T.reset_index()
                features_df.columns = ["feature", "value"]
                st.write("**📌 Fitur URL yang Dianalisis**")
                st.dataframe(features_df, use_container_width=True)

                importance_df = top_model_features(artifact)
                if not importance_df.empty:
                    st.write("**🧠 Fitur Paling Berpengaruh pada Prediksi**")
                    st.bar_chart(importance_df)

with batch_tab:
    st.subheader("📋 Analisis Batch")
    uploaded_file = st.file_uploader("📂 Upload file CSV untuk analisis massal", type=["csv"])
    st.caption("Format kolom: url (wajib), subject dan body (opsional)")
    if uploaded_file and artifact is None:
        st.error(f"Model belum ditemukan di {model_path}. Train model terlebih dahulu.")
    elif uploaded_file:
        input_df = pd.read_csv(uploaded_file)
        temp_path = Path("reports/uploaded_batch.csv")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        input_df.to_csv(temp_path, index=False)
        results = predict_batch(str(temp_path), model_path, "reports/batch_predictions.csv")

        def color_prediction(value):
            return "background-color: #fee2e2" if value == 1 else "background-color: #dcfce7"

        st.dataframe(results.style.applymap(color_prediction, subset=["prediction"]), use_container_width=True)
        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Unduh Hasil Analisis", csv, "batch_predictions.csv", "text/csv")
