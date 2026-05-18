from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
import streamlit as st

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
        return {"Model type": "not loaded", "Training date": "n/a", "Feature count": 0}
    mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "Model type": artifact.get("model_type", "unknown"),
        "Training date": artifact.get("training_date", mtime),
        "Feature count": len(artifact.get("feature_names", [])),
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
st.caption("Hybrid phishing classification using URL structural features and optional email NLP")
st.warning(
    "Aplikasi ini tidak membuka URL, tidak crawling, dan tidak melakukan request ke target. "
    "Prediksi hanya alat bantu klasifikasi edukatif, bukan verdict keamanan final."
)

model_path = st.sidebar.text_input("Model path", value=DEFAULT_MODEL_PATH)
artifact = ensure_demo_model(model_path)
st.sidebar.subheader("Model Info")
for key, value in get_model_info(model_path, artifact).items():
    st.sidebar.write(f"**{key}:** {value}")

single_tab, batch_tab = st.tabs(["Single Analysis", "Batch Analysis"])

with single_tab:
    input_col, result_col = st.columns([1, 1])

    with input_col:
        st.subheader("Input")
        url = st.text_input("URL", placeholder="https://example.com")
        with st.expander("Email content (optional)"):
            subject = st.text_input("Subject", placeholder="Account verification notice")
            body = st.text_area("Body", placeholder="Paste email text here if available")
        analyze = st.button("Analyze", type="primary")

    with result_col:
        st.subheader("Result")
        if analyze:
            if not url.strip():
                st.error("URL wajib diisi.")
            elif artifact is None:
                st.error(f"Model belum ditemukan di {model_path}. Train model terlebih dahulu.")
            else:
                result = predict_url(url, model_path, subject=subject, body=body)
                risk_score = result["risk_score"]
                render_badge("benign" if result["prediction"] == 0 else "phishing")
                st.write(f"**Risk score:** {risk_score:.2%}")
                st.progress(min(max(risk_score, 0.0), 1.0))
                st.write(f"**Risk level:** {result[risk_level]}")

                features_df = pd.DataFrame([extract_url_features(url)]).T.reset_index()
                features_df.columns = ["feature", "value"]
                st.write("**Top URL features**")
                st.dataframe(features_df, use_container_width=True)

                importance_df = top_model_features(artifact)
                if not importance_df.empty:
                    st.write("**Top model contributing features**")
                    st.bar_chart(importance_df)

with batch_tab:
    st.subheader("Batch Analysis")
    uploaded_file = st.file_uploader("Upload CSV with url or url,subject,body columns", type=["csv"])
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
        st.download_button("Download results CSV", csv, "batch_predictions.csv", "text/csv")
