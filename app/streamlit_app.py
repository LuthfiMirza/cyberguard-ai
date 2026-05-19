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

st.markdown(
    """
<style>
  .block-container { padding-top: 2rem; }
  .stButton > button { border-radius: 8px; font-weight: 600; }
  .stTextInput > div > div > input { border-radius: 8px; }
  .stTabs [data-baseweb="tab-list"] { gap: 4px; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Preparing demo model...")
def ensure_demo_model(model_path: str):
    model_file = Path(model_path)
    if not model_file.exists() and Path(DEFAULT_SAMPLE_DATASET).exists():
        train(DEFAULT_SAMPLE_DATASET, model_path, "logreg")
    if not model_file.exists():
        return None
    return joblib.load(model_path)


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


def section_header(icon: str, title: str) -> None:
    st.markdown(
        f"""
<div style="
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 1.25rem 0 0.75rem 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #D0D7DE;
">
  <span>{icon}</span>
  <span style="
    font-weight: 600;
    color: #1F2328;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  ">{title}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def result_card(prediction: int) -> None:
    if prediction == 0:
        st.markdown(
            """
<div style="
  background: #DAFBE1;
  border: 1px solid #82E09A;
  border-left: 4px solid #2DA44E;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
">
  <div style="font-size: 1.25rem; font-weight: 800; color: #116329; letter-spacing: 0.02em;">✅ AMAN</div>
  <div style="color: #1A7F37; font-size: 0.85rem; margin-top: 4px;">
    Pola URL tidak menunjukkan tanda-tanda phishing yang signifikan.
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div style="
  background: #FFEBE9;
  border: 1px solid #FFABA8;
  border-left: 4px solid #CF222E;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
">
  <div style="font-size: 1.25rem; font-weight: 800; color: #82071E; letter-spacing: 0.02em;">🚨 PHISHING TERDETEKSI</div>
  <div style="color: #CF222E; font-size: 0.85rem; margin-top: 4px;">
    URL ini memiliki pola yang mirip dengan data phishing. Berhati-hatilah.
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


def risk_score_card(risk_score: float, prediction: int, risk_level: str) -> None:
    score_color = "#2DA44E" if prediction == 0 else "#CF222E"
    bar_width = min(max(risk_score * 100, 0), 100)
    st.markdown(
        f"""
<div style="
  background: #F6F8FA;
  border: 1px solid #D0D7DE;
  border-radius: 8px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #656D76; margin-bottom: 6px; font-weight: 600;">Risk Score</div>
  <div style="font-size: 2.25rem; font-weight: 800; color: {score_color}; font-family: monospace; line-height: 1;">{risk_score:.1%}</div>
  <div style="height: 6px; background: #D0D7DE; border-radius: 999px; margin-top: 12px; overflow: hidden;">
    <div style="height: 100%; width: {bar_width:.1f}%; background: {score_color}; border-radius: 999px;"></div>
  </div>
  <div style="margin-top: 8px; font-size: 0.8rem; color: #656D76;">Risk level: <strong style="color: {score_color};">{risk_level}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state() -> None:
    st.markdown(
        """
<div style="
  background: #F6F8FA;
  border: 1px dashed #D0D7DE;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  margin-top: 1rem;
">
  <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🔍</div>
  <div style="color: #1F2328; font-weight: 600; margin-bottom: 6px; font-size: 0.95rem;">Siap menganalisis URL</div>
  <div style="color: #656D76; font-size: 0.85rem;">
    Masukkan URL di sebelah kiri, lalu klik <strong style="color: #2DA44E;">Analisis Sekarang</strong>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
<div style="padding: 1.5rem 0 1rem 0;">
  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
    <span style="font-size: 2rem;">🛡️</span>
    <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #1F2328; letter-spacing: -0.02em;">CyberGuard AI</h1>
  </div>
  <p style="color: #656D76; margin: 0; font-size: 0.9rem;">
    Deteksi phishing dari pola URL dan konten email — tanpa membuka atau mengakses target.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div style="display: flex; gap: 8px; margin-bottom: 1.25rem; flex-wrap: wrap;">
  <div style="background: #F6F8FA; border: 1px solid #D0D7DE; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; color: #656D76; display: flex; align-items: center; gap: 6px;">🔒 No URL Requests</div>
  <div style="background: #F6F8FA; border: 1px solid #D0D7DE; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; color: #656D76; display: flex; align-items: center; gap: 6px;">🚫 No Crawling</div>
  <div style="background: #F6F8FA; border: 1px solid #D0D7DE; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; color: #656D76; display: flex; align-items: center; gap: 6px;">📊 Pattern-Based Analysis</div>
</div>
""",
    unsafe_allow_html=True,
)

st.caption("_Hasil prediksi adalah alat bantu awal, bukan keputusan keamanan final._")

model_path = st.sidebar.text_input("Model path", value=DEFAULT_MODEL_PATH)
artifact = ensure_demo_model(model_path)
model_info = get_model_info(model_path, artifact)
st.sidebar.markdown("#### ℹ️ Informasi Model")
st.sidebar.markdown(f"**Tipe model:** `{model_info['Tipe model']}`")
st.sidebar.markdown(f"**Tanggal training:** `{model_info['Tanggal training']}`")
st.sidebar.markdown(f"**Jumlah fitur:** `{model_info['Jumlah fitur']}`")
st.sidebar.divider()
st.sidebar.markdown(
    """
<div style="
  background: #F6F8FA;
  border: 1px solid #D0D7DE;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.8rem;
  color: #656D76;
">
  📦 Dataset<br>
  <strong style="color: #1F2328;">507.192 URL · Kaggle</strong>
</div>
""",
    unsafe_allow_html=True,
)
st.sidebar.divider()
st.sidebar.caption("CyberGuard AI · Proyek ML Defensif")
st.sidebar.caption("Tidak melakukan request ke URL target.")

single_tab, batch_tab = st.tabs(["🔍 Analisis URL", "📋 Analisis Batch"])

with single_tab:
    input_col, result_col = st.columns([1, 1])

    with input_col:
        section_header("⌨️", "Input Analisis")
        url = st.text_input("Masukkan URL yang ingin dianalisis", placeholder="https://contoh.com/halaman")
        with st.expander("➕ Tambahkan konten email (opsional)"):
            st.caption("Menambahkan subject dan body email meningkatkan akurasi analisis.")
            subject = st.text_input("Subject", placeholder="Account verification notice")
            body = st.text_area("Body", placeholder="Paste email text here if available")
        analyze = st.button("🔍 Analisis Sekarang", type="primary")

    with result_col:
        section_header("🧪", "Hasil Analisis")
        if not analyze:
            empty_state()
        else:
            if not url.strip():
                st.error("URL wajib diisi.")
            elif artifact is None:
                st.error(f"Model belum ditemukan di {model_path}. Train model terlebih dahulu.")
            else:
                result = predict_url(url, model_path, subject=subject, body=body)
                risk_score = result["risk_score"]
                prediction = result["prediction"]
                result_card(prediction)
                risk_score_card(risk_score, prediction, result["risk_level"])

                features_df = pd.DataFrame([extract_url_features(url)]).T.reset_index()
                features_df.columns = ["feature", "value"]
                section_header("📌", "Fitur URL yang Dianalisis")
                st.dataframe(features_df, use_container_width=True)

                importance_df = top_model_features(artifact)
                if not importance_df.empty:
                    section_header("🧠", "Fitur Paling Berpengaruh")
                    st.bar_chart(importance_df)

with batch_tab:
    section_header("📋", "Analisis Batch")
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
            return "background-color: #FFEBE9; color: #CF222E" if value == 1 else "background-color: #DAFBE1; color: #116329"

        st.dataframe(results.style.applymap(color_prediction, subset=["prediction"]), use_container_width=True)
        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Unduh Hasil Analisis", csv, "batch_predictions.csv", "text/csv")
