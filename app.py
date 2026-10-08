"""
app.py
Streamlit Web Application for:
Phishing Detection System Through Hybrid Machine Learning Based on URL
Final Year B.Tech Major Project (2026)
Department of Computer Science & Engineering (Networks)
Kakatiya Institute of Technology & Science (KITSW), Warangal
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="Phishing Detection System | Hybrid ML",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Append src to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from features import FEATURE_NAMES, extract_features, get_feature_descriptions
from predict import predict_url, predict_batch

MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


@st.cache_resource
def load_cached_model():
    model_path = os.path.join(MODELS_DIR, "hybrid_model.joblib")
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)


@st.cache_data
def load_metrics():
    summary_path = os.path.join(MODELS_DIR, "metrics_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            return json.load(f)
    return None


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shield.png", width=70)
    st.title("Phishing Detection")
    st.markdown("**Hybrid Machine Learning System**")
    st.caption("Random Forest + Logistic Regression Soft Voting")
    st.divider()

    st.markdown("### 🎓 Academic Context")
    st.markdown("""
    - **Institution:** KITSW, Warangal
    - **Department:** CSE (Networks)
    - **Project Type:** B.Tech Final Year Major Project
    - **Reference:** IEEE Access (Karim et al., 2023)
    """)
    st.divider()

    st.markdown("### ⚙️ Quick URL Presets")
    sample_category = st.radio("Load Sample URL:", ["None", "Phishing Samples", "Legitimate Samples"])
    selected_sample = ""
    if sample_category == "Phishing Samples":
        selected_sample = st.selectbox("Choose Phishing URL:", [
            "http://login-verify-account-security-update.bankofamerica-online.cc/auth/login.php",
            "http://verify-paypal-identity-secure.com/webscr?cmd=_login-run&account=update",
            "http://192.168.1.100:8080/paypal/login.htm?account=update&token=489271",
            "http://appleid.apple.com-recover-account.id-security-auth.net/verify",
            "http://netflix-billing-update-suspicious-login.info/account//verify"
        ])
    elif sample_category == "Legitimate Samples":
        selected_sample = st.selectbox("Choose Legitimate URL:", [
            "https://www.google.com/search?q=cybersecurity+research",
            "https://en.wikipedia.org/wiki/Phishing",
            "https://github.com/scikit-learn/scikit-learn",
            "https://docs.python.org/3/library/urllib.parse.html",
            "https://stackoverflow.com/questions/tagged/machine-learning"
        ])


# Main Header
st.title("🛡️ Phishing Detection System Through Hybrid Machine Learning Based on URL")
st.markdown("""
*An intelligent, real-time URL inspection platform powered by a **Hybrid Voting Classifier (Random Forest + Logistic Regression)** trained on **15 lexical URL features**.*
""")

tabs = st.tabs([
    "🔍 Real-Time URL Inspector",
    "📂 Batch URL Scanner",
    "📊 Model Performance & Metrics",
    "🧠 System Architecture & Methodology"
])


# ----------------------------------------------------
# TAB 1: Real-Time URL Inspector
# ----------------------------------------------------
with tabs[0]:
    st.subheader("Single URL Classification")
    st.write("Enter a complete URL or select a preset from the sidebar to analyze its 15 lexical security features.")

    default_val = selected_sample if selected_sample else "https://www.google.com/search?q=cybersecurity+research"
    input_url = st.text_input("Enter Web URL to Analyze:", value=default_val, help="Type or paste any full URL string")

    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        analyze_btn = st.button("🚀 Analyze URL", type="primary")

    if input_url or analyze_btn:
        try:
            res = predict_url(input_url)
            verdict = res["prediction"]
            conf = res["confidence"]
            p_phish = res["phishing_probability"]
            p_legit = res["legitimate_probability"]

            st.divider()

            # Verdict Display
            if verdict == "PHISHING":
                st.error(f"""
                ### 🚨 ALERT: PHISHING URL DETECTED
                **Confidence Score:** `{conf:.2f}%`  
                This URL exhibits high-risk lexical and structural indicators characteristic of fraudulent web pages.
                """)
            else:
                st.success(f"""
                ### 🛡️ VERDICT: LEGITIMATE URL
                **Confidence Score:** `{conf:.2f}%`  
                This URL exhibits safe lexical structures adhering to recognized legitimate web domain conventions.
                """)

            # Metrics row
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(label="Predicted Verdict", value=verdict, delta="Suspicious" if verdict=="PHISHING" else "Safe")
            with m_col2:
                st.metric(label="Phishing Probability", value=f"{p_phish:.1f}%")
            with m_col3:
                st.metric(label="Legitimate Probability", value=f"{p_legit:.1f}%")

            # Progress indicator
            st.write("**Hybrid Ensemble Probability Gauge:**")
            st.progress(p_phish / 100.0)
            st.caption(f"Legitimate ({p_legit:.1f}%) ◀━━━━━━━━━━━━━━━━━━━━▶ Phishing ({p_phish:.1f}%)")

            # Risk flags
            st.subheader("⚠️ Security Risk Flags")
            if res["risk_flags"]:
                for flag in res["risk_flags"]:
                    st.warning(f"• **Risk Factor:** {flag}")
            else:
                st.info("• No high-risk structural heuristics triggered. URL structure is clean and standard.")

            # Feature Table Breakdown
            st.subheader("🔬 Extracted 15 Lexical Features Breakdown")
            desc_dict = get_feature_descriptions()

            feat_records = []
            for feat_name, val in res["features"].items():
                meta = desc_dict.get(feat_name, {"name": feat_name, "type": "-", "description": "-"})
                feat_records.append({
                    "Feature Name": meta["name"],
                    "Identifier": feat_name,
                    "Extracted Value": val,
                    "Feature Type": meta["type"],
                    "Security Significance": meta["description"]
                })

            feat_df = pd.DataFrame(feat_records)
            st.dataframe(feat_df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error analyzing URL: {e}")


# ----------------------------------------------------
# TAB 2: Batch URL Scanner
# ----------------------------------------------------
with tabs[1]:
    st.subheader("Batch URL Inspection")
    st.write("Scan multiple URLs concurrently by pasting them below or uploading a CSV file.")

    batch_input = st.text_area(
        "Paste URLs (one per line):",
        height=150,
        value="""https://www.google.com/search?q=cybersecurity
http://login-verify-account-security-update.bankofamerica-online.cc/auth/login.php
https://en.wikipedia.org/wiki/Phishing
http://192.168.1.100:8080/paypal/login.htm?account=update&token=489271
https://github.com/scikit-learn/scikit-learn
http://verify-paypal-identity-secure.com/webscr?cmd=_login-run"""
    )

    if st.button("🔍 Scan Batch URLs", type="primary"):
        urls = [u.strip() for u in batch_input.splitlines() if u.strip()]
        if urls:
            with st.spinner(f"Analyzing {len(urls)} URLs..."):
                results = predict_batch(urls)

            summary_rows = []
            for r in results:
                summary_rows.append({
                    "URL": r["url"],
                    "Verdict": r["prediction"],
                    "Confidence (%)": r["confidence"],
                    "Phishing Prob (%)": r["phishing_probability"],
                    "Legitimate Prob (%)": r["legitimate_probability"],
                    "Risk Flags Count": len(r["risk_flags"])
                })

            res_df = pd.DataFrame(summary_rows)
            st.dataframe(res_df, use_container_width=True)

            phish_count = sum(1 for r in results if r["is_phishing"])
            legit_count = len(results) - phish_count

            b_c1, b_c2, b_c3 = st.columns(3)
            b_c1.metric("Total URLs Scanned", len(results))
            b_c2.metric("Phishing Detected", phish_count)
            b_c3.metric("Legitimate Detected", legit_count)

            csv_data = res_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Batch Report (CSV)", data=csv_data, file_name="phishing_batch_scan_report.csv", mime="text/csv")


# ----------------------------------------------------
# TAB 3: Model Performance & Metrics Dashboard
# ----------------------------------------------------
with tabs[2]:
    st.subheader("Model Evaluation & Performance Benchmarks")
    metrics_data = load_metrics()

    if metrics_data:
        m = metrics_data["metrics"]
        cv = metrics_data.get("cv_scores", {})

        st.markdown("### 🏆 Comparison Table (Holdout Test Set: 2,000 URLs)")
        comp_data = {
            "Model": ["Logistic Regression", "Random Forest", "Hybrid Voting (Soft)"],
            "Accuracy": [m["logistic_regression"]["Accuracy"], m["random_forest"]["Accuracy"], m["hybrid_voting"]["Accuracy"]],
            "Precision": [m["logistic_regression"]["Precision"], m["random_forest"]["Precision"], m["hybrid_voting"]["Precision"]],
            "Recall": [m["logistic_regression"]["Recall"], m["random_forest"]["Recall"], m["hybrid_voting"]["Recall"]],
            "Specificity": [m["logistic_regression"]["Specificity"], m["random_forest"]["Specificity"], m["hybrid_voting"]["Specificity"]],
            "F1-Score": [m["logistic_regression"]["F1-Score"], m["random_forest"]["F1-Score"], m["hybrid_voting"]["F1-Score"]],
            "ROC-AUC": [m["logistic_regression"]["ROC-AUC"], m["random_forest"]["ROC-AUC"], m["hybrid_voting"]["ROC-AUC"]],
            "5-Fold CV Acc": [
                f"{cv.get('logistic_regression', {}).get('mean', 0):.4f} ± {cv.get('logistic_regression', {}).get('std', 0):.4f}",
                f"{cv.get('random_forest', {}).get('mean', 0):.4f} ± {cv.get('random_forest', {}).get('std', 0):.4f}",
                f"{cv.get('hybrid_voting', {}).get('mean', 0):.4f} ± {cv.get('hybrid_voting', {}).get('std', 0):.4f}"
            ]
        }
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp.style.format({
            "Accuracy": "{:.4f}",
            "Precision": "{:.4f}",
            "Recall": "{:.4f}",
            "Specificity": "{:.4f}",
            "F1-Score": "{:.4f}",
            "ROC-AUC": "{:.4f}"
        }), use_container_width=True, hide_index=True)

        st.markdown("""
        > **Key Takeaway:** The **Hybrid Voting Classifier (Soft Voting)** combines the high discriminative power of Random Forest with the calibrated probabilities of Logistic Regression, achieving balanced high precision (>92%) and low false alarm rates.
        """)

    st.divider()
    st.subheader("📈 Visual Performance Analytics")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("#### 1. Confusion Matrices")
        cm_file = os.path.join(REPORTS_DIR, "confusion_matrices.png")
        if os.path.exists(cm_file):
            st.image(cm_file, caption="Confusion Matrices across all 3 models", use_container_width=True)

    with p_col2:
        st.markdown("#### 2. Receiver Operating Characteristic (ROC)")
        roc_file = os.path.join(REPORTS_DIR, "roc_curves.png")
        if os.path.exists(roc_file):
            st.image(roc_file, caption="ROC Curves comparing LR, RF, and Hybrid", use_container_width=True)

    p_col3, p_col4 = st.columns(2)
    with p_col3:
        st.markdown("#### 3. Random Forest Feature Importance")
        fi_file = os.path.join(REPORTS_DIR, "feature_importance.png")
        if os.path.exists(fi_file):
            st.image(fi_file, caption="Gini Feature Importance ranking of the 15 features", use_container_width=True)

    with p_col4:
        st.markdown("#### 4. Model Metric Bar Comparison")
        mc_file = os.path.join(REPORTS_DIR, "model_comparison.png")
        if os.path.exists(mc_file):
            st.image(mc_file, caption="Accuracy, Precision, Recall, F1, and AUC Comparison", use_container_width=True)


# ----------------------------------------------------
# TAB 4: Architecture & Methodology
# ----------------------------------------------------
with tabs[3]:
    st.subheader("System Architecture & Mathematical Formulation")

    st.markdown("""
    ### 1. Proposed Methodology Workflow
    The end-to-end detection architecture operates through six sequential phases:
    1. **Data Acquisition:** 10,000 balanced URLs collected from PhishTank (phishing) and Tranco (legitimate).
    2. **Lexical Feature Extraction:** Fast string parsing converts any URL into a 15-dimensional numeric vector.
    3. **Stratified Partitioning & Leakage Prevention:** 80/20 train/test split. `StandardScaler` is fitted strictly on `X_train`.
    4. **Base Estimator Optimization:**
       - **Random Forest:** Non-linear decision tree bagging with subspace randomization.
       - **Logistic Regression:** Linear model with convex log-loss and $L_2$ regularization.
    5. **Hybrid Voting Integration:** Combines models via Soft Voting (weighted posterior averaging).
    6. **Inference & Explainability:** Generates classification verdict, calibrated confidence score, and triggered security risk flags.
    """)

    st.markdown("""
    ### 2. Mathematical Formulations

    #### A. Random Forest Classifier
    For a given decision tree node, splitting decisions use **Gini Impurity** or **Entropy**:
    $$E(S) = -\\sum_{i=1}^{c} p_i \\log_2 p_i$$
    $$G(S) = 1 - \\sum_{i=1}^{c} p_i^2$$
    The ensemble prediction averages $B$ bootstrap trees:
    $$F(x) = \\frac{1}{B} \\sum_{b=1}^{B} f_b(x)$$

    #### B. Logistic Regression Classifier
    Maps linear combinations of scaled features to probabilities using the standard logistic sigmoid:
    $$P(y=1|x) = \\sigma(w^T x + b) = \\frac{1}{1 + e^{-(w^T x + b)}}$$
    Optimized by minimizing the regularized negative log-likelihood (log-loss):
    $$J(w) = -\\frac{1}{m} \\sum_{i=1}^{m} \\left[ y^{(i)} \\ln(\\hat{y}^{(i)}) + (1 - y^{(i)}) \\ln(1 - \\hat{y}^{(i)}) \\right] + \\frac{\\lambda}{2m} \\|w\\|_2^2$$

    #### C. Hybrid Soft Voting Ensemble
    Computes the weighted posterior probability across both base models:
    $$P_{hybrid}(y=1|x) = w_{RF} \\cdot P_{RF}(y=1|x) + w_{LR} \\cdot P_{LR}(y=1|x)$$
    $$\\hat{y} = \\begin{cases} 1 & \\text{if } P_{hybrid}(y=1|x) \\ge 0.50 \\\\ 0 & \\text{otherwise} \\end{cases}$$

    ---

    ### 3. Project Information & Credits
    - **Academic Institution:** Kakatiya Institute of Technology & Science (KITSW), Warangal
    - **Department:** Computer Science & Engineering (Networks)
    - **Supervisor:** S. Ravi
    - **Coordinator:** Dr. A. Godavari
    - **Team Members:** Pasula Udaya, Sadiya Masarrath, Pulugu Kumar Reddy, Sampangi Nithin, Penchala Hansika
    - **Primary Benchmark Reference:** Karim, A. et al., *"Phishing Detection System Through Hybrid Machine Learning Based on URL"*, IEEE Access, vol. 11, pp. 36805–36822, 2023.
    """)
