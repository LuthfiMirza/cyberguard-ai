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
  .stApp {
    background-color: #0D1117;
    color: #E6EDF3;
  }

  section[data-testid="stSidebar"] {
    background-color: #161B22;
    border-right: 1px solid #30363D;
  }

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    background-color: #161B22;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
  }

  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: #00FFA3;
    box-shadow: 0 0 0 2px rgba(0, 255, 163, 0.15);
  }

  .stButton > button {
    background: linear-gradient(135deg, #00FFA3, #00C77A);
    color: #0D1117;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.4rem;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    transition: all 0.2s ease;
  }

  .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0, 255, 163, 0.35);
  }

  .stTabs [data-baseweb="tab-list"] {
    background-color: #161B22;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #30363D;
  }

  .stTabs [data-baseweb="tab"] {
    color: #8B949E;
    border-radius: 6px;
    font-weight: 500;
  }

  .stTabs [aria-selected="true"] {
    background-color: #0D1117;
    color: #00FFA3;
  }

  .stDataFrame {
    border: 1px solid #30363D;
    border-radius: 8px;
  }

  [data-testid="stMetric"] {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 1rem;
  }

  .stCaption, caption, small {
    color: #8B949E;
  }

  .streamlit-expanderHeader {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    color: #8B949E;
  }

  .stProgress > div > div {
    background: linear-gradient(90deg, #00FFA3, #58A6FF);
    border-radius: 999px;
  }

  hr {
    border-color: #30363D;
  }

  [data-testid="stFileUploader"] {
    background-color: #161B22;
    border: 1px dashed #30363D;
    border-radius: 8px;
  }

  label, .stMarkdown, .stTextInput label, .stTextArea label {
    color: #E6EDF3 !important;
  }
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
        return {"Tipe Model": "not loaded", "Tanggal Training": "n/a", "Jumlah Fitur": 0}
    mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Tipe Model": artifact.get("model_type", "unknown"),
        "Tanggal Training": artifact.get("training_date", mtime),
        "Jumlah Fitur": len(artifact.get("feature_names", [])),
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
  margin: 1.5rem 0 0.75rem 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #30363D;
">
  <span style="color: #00FFA3;">{icon}</span>
  <span style="font-weight: 600; color: #E6EDF3; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.05em;">
    {title}
  </span>
</div>
""",
        unsafe_allow_html=True,
    )


def result_card(prediction: int) -> None:
    if prediction == 0:
        st.markdown(
            """
<div style="
  background: rgba(0, 255, 163, 0.08);
  border: 1px solid rgba(0, 255, 163, 0.3);
  border-left: 4px solid #00FFA3;
  border-radius: 8px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1rem;
">
  <div style="font-size: 1.4rem; font-weight: 800; color: #00FFA3; letter-spacing: 0.05em;">
    ✅ AMAN
  </div>
  <div style="color: #8B949E; font-size: 0.875rem; margin-top: 4px;">
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
  background: rgba(255, 68, 68, 0.08);
  border: 1px solid rgba(255, 68, 68, 0.3);
  border-left: 4px solid #FF4444;
  border-radius: 8px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1rem;
">
  <div style="font-size: 1.4rem; font-weight: 800; color: #FF4444; letter-spacing: 0.05em;">
    🚨 PHISHING TERDETEKSI
  </div>
  <div style="color: #8B949E; font-size: 0.875rem; margin-top: 4px;">
    URL ini memiliki pola yang mirip dengan data phishing. Berhati-hatilah.
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


def risk_score_card(risk_score: float, prediction: int) -> None:
    color = "#00FFA3" if prediction == 0 else "#FF4444"
    width = min(max(risk_score * 100, 0), 100)
    st.markdown(
        f"""
<div style="
  background: #161B22;
  border: 1px solid #30363D;
  border-radius: 8px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1rem;
">
  <div style="color: #8B949E; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;">
    Risk Score
  </div>
  <div style="font-size: 2.5rem; font-weight: 800; color: {color}; font-family: monospace;">
    {risk_score:.1%}
  </div>
  <div style="
    height: 6px;
    background: #30363D;
    border-radius: 999px;
    margin-top: 12px;
    overflow: hidden;
  ">
    <div style="
      height: 100%;
      width: {width:.1f}%;
      background: linear-gradient(90deg, {color}, {color}88);
      border-radius: 999px;
      transition: width 0.5s ease;
    "></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state() -> None:
    st.markdown(
        """
<div style="
  background: #161B22;
  border: 1px dashed #30363D;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  margin-top: 2rem;
">
  <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
  <div style="color: #E6EDF3; font-weight: 600; margin-bottom: 8px;">
    Siap menganalisis URL
  </div>
  <div style="color: #8B949E; font-size: 0.875rem;">
    Masukkan URL di sebelah kiri, lalu klik <strong style="color: #00FFA3;">Analisis Sekarang</strong>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def sidebar_info_item(label: str, value: str | int) -> None:
    st.sidebar.markdown(
        f"""
<div style="margin-bottom: 0.75rem;">
  <div style="font-size: 0.75rem; color: #8B949E; margin-bottom: 2px;">{label}</div>
  <div style="font-family: monospace; color: #00FFA3; font-weight: 600;">{value}</div>
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown(
    """
<div style="padding: 2rem 0 1rem 0;">
  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
    <span style="font-size: 2.5rem;">🛡️</span>
    <h1 style="
      margin: 0;
      font-size: 2.2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #00FFA3, #58A6FF);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -0.02em;
    ">CyberGuard AI</h1>
  </div>
  <p style="color: #8B949E; margin: 0; font-size: 0.95rem;">
    Deteksi phishing dari pola URL dan konten email — tanpa membuka atau mengakses target.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div style="display: flex; gap: 12px; margin-bottom: 1rem; flex-wrap: wrap;">
  <div style="background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 0.5rem 1rem; display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #8B949E;">
    <span style="color: #00FFA3;">🔒</span> No URL Requests
  </div>
  <div style="background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 0.5rem 1rem; display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #8B949E;">
    <span style="color: #00FFA3;">🚫</span> No Crawling
  </div>
  <div style="background: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 0.5rem 1rem; display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #8B949E;">
    <span style="color: #58A6FF;">📊</span> Pattern-Based Analysis
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.caption("_Hasil prediksi adalah alat bantu awal, bukan keputusan keamanan final._")

model_path = st.sidebar.text_input("Model path", value=DEFAULT_MODEL_PATH)
artifact = ensure_demo_model(model_path)
st.sidebar.markdown(
    """
<div style="padding: 1rem 0 0.5rem 0; border-bottom: 1px solid #30363D; margin-bottom: 1rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #8B949E;">
    ℹ️ Informasi Model
  </div>
</div>
""",
    unsafe_allow_html=True,
)
for key, value in get_model_info(model_path, artifact).items():
    sidebar_info_item(key, value)
st.sidebar.markdown(
    """
<div style="background:#0D1117;border:1px solid #30363D;border-radius:8px;padding:0.8rem;margin-top:1rem;">
  <div style="font-size:0.75rem;color:#8B949E;margin-bottom:2px;">Dataset</div>
  <div style="font-family:monospace;color:#58A6FF;font-weight:600;">507.192 URL · Kaggle</div>
</div>
<hr>
<div style="color:#8B949E;font-size:0.78rem;line-height:1.5;">
  CyberGuard AI · Proyek ML Defensif<br>
  Tidak melakukan request ke URL target.
</div>
""",
    unsafe_allow_html=True,
)

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
                risk_score_card(risk_score, prediction)
                st.markdown(
                    f"""
<div style="color:#8B949E;font-family:monospace;margin-bottom:1rem;">
  Risk level: <span style="color:#E6EDF3;font-weight:700;">{result['risk_level']}</span>
</div>
""",
                    unsafe_allow_html=True,
                )

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
            return "background-color: #2d1f1f; color: #FF4444" if value == 1 else "background-color: #10251d; color: #00FFA3"

        st.dataframe(results.style.applymap(color_prediction, subset=["prediction"]), use_container_width=True)
        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Unduh Hasil Analisis", csv, "batch_predictions.csv", "text/csv")
