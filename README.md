# Phishing Detection System Through Hybrid Machine Learning Based on URL

**Final Year B.Tech Major Project**  
*Department of Computer Science & Engineering (Networks)*  
*Kakatiya Institute of Technology & Science (KITSW), Warangal*  
*Academic Year: 2025–2026*

---

## 📌 Project Overview
Phishing attacks remain one of the most critical and financially devastating cyber threats on the Internet. Fraudulent websites impersonate reputable organizations—such as banks, payment processors, and cloud service providers—to harvest credentials, steal payment card numbers, and distribute malware.

Traditional security measures (such as IP/domain blacklists) fail to defend against **zero-day phishing attacks**, as new phishing domains are generated automatically and discarded before blacklists update.

This project delivers an automated, high-precision **Phishing Detection System** powered by a **Hybrid Machine Learning Voting Ensemble (Random Forest + Logistic Regression)** trained on **15 lexical URL features**. The system operates entirely on the URL string structure without downloading web page content or requiring third-party API queries, enabling **instant, privacy-preserving, real-time protection**.

---

## 🚀 Key Features
- **15 Lexical URL Features:** Extracted purely from the raw URL string (length, host length, subdomains, suspicious tokens, IP host, redirection flags, etc.).
- **Hybrid Soft Voting Classifier:** Combines non-linear tree bagging (**Random Forest**) with regularized, calibrated probabilistic modeling (**Logistic Regression**).
- **Leakage-Free ML Pipeline:** Strict stratified 80/20 train/test split with feature scaling fitted exclusively on training folds.
- **Hyperparameter Optimization:** Automated tuning via `GridSearchCV` and 5-Fold Stratified Cross-Validation.
- **Comprehensive Visual Analytics:** Automated generation of Confusion Matrices, ROC-AUC curves, Feature Importance rankings, and model metric comparisons.
- **Interactive Streamlit Web App:** Real-time URL inspector with risk factor badges, confidence scoring, batch CSV scanning, and downloadable reports.
- **CLI Prediction Tool & Test Suite:** Built-in test suite evaluating representative phishing and legitimate URLs.

---

## 🗂️ Project Directory Structure

```text
Major_Project/
├── data/
│   ├── dataset.csv               # Balanced 10,000 URL benchmark (PhishTank + Tranco)
│   └── extracted_features.csv    # Pre-computed 15 lexical features matrix
├── models/
│   ├── hybrid_model.joblib       # Trained Soft Voting Ensemble model
│   ├── random_forest_model.joblib# Tuned Random Forest model
│   ├── logistic_regression_model.joblib # Tuned Logistic Regression model
│   ├── scaler.joblib             # Fitted StandardScaler
│   ├── feature_names.joblib      # List of the 15 feature column names
│   └── metrics_summary.json      # Complete evaluation metrics in JSON format
├── notebooks/
│   └── phishing_detection.ipynb  # End-to-end Jupyter Notebook with full analysis
├── reports/
│   ├── confusion_matrices.png    # Confusion matrix heatmaps for all 3 models
│   ├── roc_curves.png            # Receiver Operating Characteristic comparison
│   ├── feature_importance.png    # Random Forest Gini feature importances
│   └── model_comparison.png      # Bar chart comparison across evaluation metrics
├── src/
│   ├── __init__.py
│   ├── download_data.py          # Script to acquire and clean benchmark dataset
│   ├── features.py               # Extraction logic for the 15 lexical URL features
│   ├── train.py                  # End-to-end ML training, tuning, and evaluation
│   ├── predict.py                # CLI inference tool and 10-URL test suite
│   └── generate_notebook.py      # Script to rebuild the Jupyter Notebook
├── app.py                        # Streamlit Web Application
├── requirements.txt              # Project dependencies
└── README.md                     # Documentation and setup instructions
```

---

## 🔬 The 15 Extracted Lexical Features

| # | Feature Name | Code Identifier | Type | Cyber Security Significance & Rationale |
|---|--------------|-----------------|------|-----------------------------------------|
| 1 | **URL Length** | `url_length` | Numeric | Phishing URLs often use lengthy parameters or embedded tokens to conceal destinations. |
| 2 | **Hostname Length** | `hostname_length` | Numeric | Attackers craft elongated domains spoofing trusted brands (e.g., `bank-login-update-auth.com`). |
| 3 | **Number of Dots** | `num_dots` | Numeric | Excessive dots indicate nested subdomains engineered to mislead users. |
| 4 | **Number of Hyphens** | `num_hyphens` | Numeric | Hyphens are widely utilized in typosquatting and fake brand conjunctions. |
| 5 | **Number of '@' Symbols** | `num_at` | Numeric | Browsers discard all characters before the `@` symbol, connecting to the host following it. |
| 6 | **Number of Digits** | `num_digits` | Numeric | Phishing links embed numeric session IDs, timestamps, or hex encoded payloads. |
| 7 | **Special Characters** | `num_special_chars` | Numeric | Count of `?`, `=`, `&`, `%`, `_`, `~`, `+`, `#`, `!`, `$`, `;` reflecting query manipulation. |
| 8 | **Presence of IP Address** | `has_ip` | Binary (0/1) | Legitimate websites rarely use raw IP addresses (e.g. `http://192.168.1.1`) as public hostnames. |
| 9 | **HTTPS Usage** | `has_https` | Binary (0/1) | Identifies whether the scheme uses HTTPS encryption. |
| 10 | **Number of Subdomains** | `num_subdomains` | Numeric | Counts subdomain levels beyond root and TLD (e.g., `verify.login.paypal.com.attacker.net`). |
| 11 | **Path Levels (Depth)** | `num_path_levels` | Numeric | Directory hierarchy depth in the URL path. Phishing sites often nest deep directory trees. |
| 12 | **Suspicious Keywords** | `suspicious_keyword` | Binary (0/1) | Detects target authentication tokens: `login`, `verify`, `secure`, `update`, `bank`, `account`, `signin`. |
| 13 | **URL Shortener Service** | `is_shortened` | Binary (0/1) | Flags known shortening services (e.g., `bit.ly`, `tinyurl.com`, `t.co`) masking the final destination. |
| 14 | **'//' Redirection in Path**| `has_double_slash_redirect` | Binary (0/1) | Detects `//` inside path or parameters, indicating open redirect and proxy evasion attacks. |
| 15 | **Presence of Port Number**| `has_port` | Binary (0/1) | Flags explicit non-standard network ports (e.g., `:8080`, `:8443`) in the network location. |

---

## 📊 Experimental Results & Comparison

Evaluated on the **hold-out 20% test partition (2,000 URLs: 1,000 Legitimate, 1,000 Phishing)**:

| Model Architecture | Accuracy | Precision | Recall (Sensitivity) | Specificity | F1-Score | ROC-AUC | 5-Fold CV Accuracy |
|--------------------|:--------:|:---------:|:--------------------:|:-----------:|:--------:|:-------:|:------------------:|
| **Logistic Regression (LR)** | 82.45% | 84.93% | 78.90% | 86.00% | 81.80% | 90.88% | 83.81% (±0.0121) |
| **Random Forest (RF)** | 92.90% | 93.69% | 92.00% | 93.80% | 92.84% | 97.70% | 92.34% (±0.0051) |
| **Hybrid Voting (Soft)** ⭐ | **90.65%** | **92.74%** | **88.20%** | **93.10%** | **90.42%** | **96.37%** | **90.56% (±0.0032)** |
| **Hybrid Voting (Hard)** | 86.90% | 91.24% | 81.60% | 92.20% | 85.62% | N/A | 86.95% (±0.0064) |

### 🔍 Soft Voting vs. Hard Voting Comparison
- **Hard Voting** operates as a strict majority decision rule: $\hat{y} = \text{mode}(C_{RF}, C_{LR})$. It discards classification margin confidence, causing edge-case tie penalties and lower sensitivity.
- **Soft Voting** averages the posterior predicted class probabilities:
  $$P_{hybrid}(y=1|x) = \frac{P_{RF}(y=1|x) + P_{LR}(y=1|x)}{2}$$
- **Result:** Soft Voting achieves **+3.75% higher accuracy**, **+4.80% higher F1-score**, produces reliable confidence percentages, and allows threshold tuning.

---

## 🌲 Feature Importance Ranking (Random Forest)

Based on Mean Decrease in Gini Impurity:

1. **`url_length`** (23.74%) — Total URL string character length
2. **`has_https`** (16.96%) — HTTPS protocol security scheme
3. **`hostname_length`** (14.41%) — Domain and host character length
4. **`num_path_levels`** (12.52%) — Directory hierarchy depth
5. **`num_digits`** (12.21%) — Numeric token density
6. **`num_dots`** (4.51%) — Dot frequency in domain and path
7. **`num_special_chars`** (4.43%) — Obfuscation symbol count
8. **`num_hyphens`** (3.84%) — Typosquatting hyphen density
9. **`num_subdomains`** (3.29%) — Domain hierarchy levels
10. **`suspicious_keyword`** (2.73%) — Presence of authentication tokens
11. **`is_shortened`** (0.64%) — Redirection services
12. **`num_at`** (0.46%) — Credential `@` indicator
13. **`has_double_slash_redirect`** (0.15%) — Open redirect indicator
14. **`has_ip`** (0.07%) — Raw IP address usage
15. **`has_port`** (0.04%) — Non-standard network port

---

## 🧪 Built-in Test Suite Results (10 Representative URLs)

```text
================================================================================
                PHISHING DETECTION SYSTEM - SAMPLE URL TEST SUITE
================================================================================

Test 01: [PASS]
  URL:        https://www.google.com/search?q=cybersecurity+research
  Expected:   LEGITIMATE
  Predicted:  LEGITIMATE (Confidence: 80.53%)

Test 02: [PASS]
  URL:        https://en.wikipedia.org/wiki/Phishing
  Expected:   LEGITIMATE
  Predicted:  LEGITIMATE (Confidence: 88.34%)

Test 03: [PASS]
  URL:        https://github.com/scikit-learn/scikit-learn
  Expected:   LEGITIMATE
  Predicted:  LEGITIMATE (Confidence: 96.74%)

Test 04: [PASS]
  URL:        https://docs.python.org/3/library/urllib.parse.html
  Expected:   LEGITIMATE
  Predicted:  LEGITIMATE (Confidence: 90.54%)

Test 05: [PASS]
  URL:        https://stackoverflow.com/questions/tagged/machine-learning
  Expected:   LEGITIMATE
  Predicted:  LEGITIMATE (Confidence: 72.15%)

Test 06: [PASS]
  URL:        http://login-verify-account-security-update.bankofamerica-online.cc/auth/login.php
  Expected:   PHISHING
  Predicted:  PHISHING (Confidence: 98.04%)
  Flags:      Contains sensitive keywords, High hyphen frequency, Abnormally long URL

Test 07: [PASS]
  URL:        http://verify-paypal-identity-secure.com/webscr?cmd=_login-run&account=update
  Expected:   PHISHING
  Predicted:  PHISHING (Confidence: 97.26%)
  Flags:      Contains sensitive keywords, High hyphen frequency, Abnormally long URL

Test 08: [PASS]
  URL:        http://192.168.1.100:8080/paypal/login.htm?account=update&token=489271
  Expected:   PHISHING
  Predicted:  PHISHING (Confidence: 99.87%)
  Flags:      Host is an IP address, Contains sensitive keywords, Non-standard port

Test 09: [PASS]
  URL:        http://appleid.apple.com-recover-account.id-security-auth.net/verify
  Expected:   PHISHING
  Predicted:  PHISHING (Confidence: 99.38%)
  Flags:      Contains sensitive keywords, Excessive subdomain depth, High hyphen frequency

Test 10: [PASS]
  URL:        http://netflix-billing-update-suspicious-login.info/account//verify
  Expected:   PHISHING
  Predicted:  PHISHING (Confidence: 97.99%)
  Flags:      Contains '//' redirection, Contains sensitive keywords, High hyphen frequency

================================================================================
Test Summary: 10 / 10 Passed (100.0%)
================================================================================
```

---

## 🛠️ Installation and Execution Guide

### 1. Prerequisites
- Python 3.10+ or Python 3.11+
- Virtual environment (recommended)

### 2. Setup Environment
```powershell
# Clone or navigate to the workspace
cd C:\Major_Project

# Create and activate a virtual environment (optional)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

### 3. Re-train Models (Optional)
To fetch the benchmark data and retrain all models from scratch:
```powershell
# Step 1: Download & prepare the balanced dataset (10,000 URLs)
python src/download_data.py

# Step 2: Train, tune, cross-validate, and evaluate all models
python src/train.py
```

### 4. Run CLI Predictions
Test individual URLs or run the built-in test suite:
```powershell
# Run the 10-URL sample test suite
python src/predict.py --test

# Test any custom URL
python src/predict.py --url "http://paypal-verification-account-update.xyz/login.php"
```

### 5. Launch the Streamlit Web Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501` to access the interactive web interface.

### 6. Run the Jupyter Notebook
```powershell
jupyter notebook notebooks/phishing_detection.ipynb
```

---

## 👥 Project Team & Supervision
- **Institution:** Kakatiya Institute of Technology & Science (KITSW), Warangal
- **Department:** Computer Science & Engineering (Networks)
- **Course:** B.Tech Final Year Major Project (2026)
- **Supervisor:** S. Ravi
- **Coordinator:** Dr. A. Godavari
- **Team Members:**
  - Pasula Udaya
  - Sadiya Masarrath
  - Pulugu Kumar Reddy
  - Sampangi Nithin
  - Penchala Hansika

---

## 📚 Primary Academic Reference
> **[1]** Abdul Karim, Mobeen Shahroz, Khabib Mustofa, Samir Brahim Belhaouari, and S. Ramana Kumar Joga, *"Phishing Detection System Through Hybrid Machine Learning Based on URL,"* **IEEE Access**, vol. 11, pp. 36805–36822, 2023. DOI: `10.1109/ACCESS.2023.3252366`.
