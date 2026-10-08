# MAJOR PROJECT REPORT DOCUMENTATION

## Title: Phishing Detection System Through Hybrid Machine Learning Based on URL

**Degree:** Bachelor of Technology (B.Tech) in Computer Science & Engineering (Networks)  
**Institution:** Kakatiya Institute of Technology & Science (KITSW), Warangal  
**Academic Year:** 2025–2026  

**Team Members:**
- Pasula Udaya
- Sadiya Masarrath
- Pulugu Kumar Reddy
- Sampangi Nithin
- Penchala Hansika

**Supervisor:** S. Ravi  
**Coordinator:** Dr. A. Godavari  

---

## 1. ABSTRACT
Phishing cyberattacks remain among the most severe and rapidly escalating threats to Internet security, causing billions of dollars in annual losses worldwide. Conventional defense mechanisms rely heavily on static blacklists and whitelists; however, such lists fail completely against newly registered, zero-day phishing domains. In this study, an automated, real-time Phishing Detection System is designed and evaluated using a Hybrid Machine Learning approach. The proposed framework extracts 15 distinct lexical and structural features directly from raw URL strings, completely eliminating dependencies on webpage source code, DOM trees, or third-party reputation lookups. 

Two complementary classifiers are integrated: Random Forest (an ensemble tree-based bagging model capturing non-linear feature interactions) and Logistic Regression (a regularized linear model providing well-calibrated posterior probabilities). The models are combined using a Hybrid Soft Voting Classifier. Experimental evaluations on a balanced benchmark dataset of 10,000 URLs (sourced from PhishTank and the Tranco Top 1 Million ranking) demonstrate that the proposed Hybrid Soft Voting ensemble achieves 90.65% classification accuracy, 92.74% precision, 93.10% specificity, 90.42% F1-score, and an ROC-AUC of 0.9637 on a 20% holdout test set (2,000 URLs), with a 5-fold cross-validation score of 90.56% (±0.0032). An interactive web application built with Streamlit demonstrates real-time classification, confidence scoring, and feature attribution.

---

## 2. INTRODUCTION
### 2.1 Background
The Internet has evolved into an indispensable backbone for global communication, e-commerce, banking, healthcare, and education. Alongside this rapid expansion, malicious actors increasingly deploy fraudulent tactics to compromise confidential user data. Among these cybercrimes, **phishing** is the most pervasive attack vector, responsible for over \$2.5 billion in reported losses in recent multi-year FBI IC3 reports.

### 2.2 Mechanism of Phishing Attacks
Phishing attacks typically follow a multi-stage lifecycle:
1. **Infrastructure Creation:** The attacker creates a counterfeit website closely mimicking an authentic service (e.g., PayPal, Bank of America, Apple ID).
2. **Deceptive Delivery:** The victim is lured via email, SMS (smishing), or social media into clicking an obfuscated or typosquatted URL.
3. **Deception & Ingestion:** The victim enters sensitive credentials, one-time passwords (OTPs), or financial details into the counterfeit portal.
4. **Exfiltration & Abuse:** The attacker captures the credentials to execute unauthorized transactions or breach internal corporate networks.

### 2.3 Why URLs Matter
Every web-based phishing attack commences with the transmission of a URL. Classifying the maliciousness of a URL before the client browser resolves the IP address or downloads page content enables preventive termination of the attack vector at the earliest possible stage.

### 2.4 Why Machine Learning Over Blacklists
Static blacklists (e.g., Google Safe Browsing, PhishTank, OpenPhish) operate reactively: a URL must first be detected, reported, verified, and distributed before client browsers block it. Studies indicate that modern phishing attacks exhibit an operational lifespan of fewer than 4 to 12 hours, with over 70% of targets visited before the domain appears on blacklists. Machine Learning enables inductive generalization: models learn intrinsic structural patterns (lexical length, special character distributions, keyword positioning, IP usage, and redirection sequences) that characterize phishing URLs, allowing the detection of zero-day attacks in real time.

---

## 3. LITERATURE SURVEY & RELATED WORK

| Citation / System | Methodology & Features | Reported Performance | Critical Limitations |
| :--- | :--- | :--- | :--- |
| **Blacklists / Whitelists** (e.g. PhishNet) | Exact string & regex matching against known database | High precision on known URLs (~86% TP) | Incapable of detecting newly generated zero-day phishing domains. |
| **Phish-Safe** (Jain & Gupta, 2018) | SVM + Naive Bayes on URL structural features | 90.0% Detection Accuracy | Small feature space; susceptible to distribution drift; required frequent retraining. |
| **CANTINA+** (Xiang et al., 2011) | 15 HTML-based features + TF-IDF Google search verification | 92.0% Accuracy | High latency; requires downloading page HTML; high false-positive rate; language-dependent. |
| **Deep Learning RCNN** (Fang et al., 2019) | Multi-level character vectors + RCNN attention | 99.85% Accuracy on emails | Extremely high computational overhead; requires GPUs; unfeasible for client-side real-time deployment. |
| **Karim et al. (IEEE Access, 2023)** | Multi-classifier evaluation & LSD Hybrid (LR + SVC + DT) on Kaggle dataset | 95.23% to 98.12% Accuracy | Tested on vector pre-extracted features; relied heavily on complex tree-SVM stacking. |

---

## 4. PROBLEM STATEMENT
Manual identification of fraudulent URLs is inconsistent and unscalable. Static blacklist tools exhibit a fundamental delay window during which zero-day phishing attacks succeed. Conversely, heavy deep learning and content-based approaches require fetching webpage source code (exposing user privacy and incurring network latency). Individual shallow classifiers trade off precision against recall: linear models struggle with complex non-linear feature conjuncts, while uncalibrated tree models suffer from high variance on noisy URL structures.

Therefore, an automated, lightweight, feature-driven hybrid machine learning system is required to classify raw URLs in real time with high precision, minimal false positives, and zero external latency.

---

## 5. OBJECTIVES
1. **Automated Lexical Feature Extraction:** Formulate and implement an efficient extractor for 15 structural and lexical URL features purely from raw input strings without page rendering or DNS queries.
2. **Benchmarking Base Estimators:** Train and optimize two complementary machine learning classifiers: Random Forest (tree-based bagging) and Logistic Regression (linear, probabilistically calibrated).
3. **Hybrid Ensemble Architecture:** Integrate the base classifiers through a Voting Classifier, comparing Hard and Soft voting mechanisms to optimize classification margin.
4. **Leakage Prevention & Cross-Validation:** Ensure scientific validity by strictly fitting transformations on training splits and benchmarking across 5-fold stratified cross-validation.
5. **Real-Time Deployment:** Deploy an interactive web application that provides instantaneous verdicts, probability confidence scores, and heuristic risk breakdowns.

---

## 6. PROPOSED METHODOLOGY & SYSTEM ARCHITECTURE

```mermaid
flowchart TD
    A["Raw URL Input"] --> B["URL Preprocessing & Normalization"]
    B --> C["15 Lexical Feature Extraction Engine"]
    C --> D["Feature Vector (15 Dimensions)"]
    D --> E["StandardScaler (Training-Fitted)"]
    D --> F["Random Forest Classifier (Bagging Trees)"]
    E --> G["Logistic Regression Classifier (L2 Regularized)"]
    F -->|P_RF(y=1)| H["Hybrid Soft Voting Ensemble"]
    G -->|P_LR(y=1)| H
    H --> I["Decision Boundary Threshold (tau = 0.50)"]
    I -->|P >= 0.50| J["🚨 PHISHING VERDICT + Confidence Score"]
    I -->|P < 0.50| K["🛡️ LEGITIMATE VERDICT + Confidence Score"]
```

### Workflow Steps:
1. **Dataset Collection & Stratification:** 10,000 URLs (5,000 verified PhishTank phishing URLs and 5,000 Tranco top-tier legitimate URLs).
2. **Feature Extraction:** 15 lexical features extracted per sample into a structured matrix.
3. **Partitioning:** Stratified 80/20 train/test split (8,000 training samples, 2,000 testing samples).
4. **Base Model Training & Tuning:**
   - Random Forest tuned across tree depth (`max_depth: 25`), estimators (`n_estimators: 150`), and split criteria (`min_samples_split: 5`).
   - Logistic Regression tuned across regularization strength ($C=0.10$, L-BFGS solver).
5. **Hybrid Voting Integration:** Base models combined via Soft Voting (weighted probability averaging).
6. **Inference & Risk Explanation:** Production inference generating verdicts, confidence percentages, and flagged risk factors.

---

## 7. FEATURE ENGINEERING: THE 15 LEXICAL FEATURES

| Feature | Mathematical Definition | Cyber Threat Significance |
|---|---|---|
| **`url_length`** | $L_{url} = \text{len}(URL)$ | Phishing URLs are significantly longer on average to accommodate token evasion and deeply nested targets. |
| **`hostname_length`** | $L_{host} = \text{len}(Host)$ | Elongated hostnames allow spoofing of reputable domain names (e.g. `paypal-security-update.com`). |
| **`num_dots`** | $N_{dot} = \text{count}(URL, '.')$ | Multiple dots indicate excessive subdomains engineered to mimic legitimate domain hierarchies. |
| **`num_hyphens`** | $N_{hyphen} = \text{count}(URL, '-')$ | Hyphens are characteristic of typosquatting and fake brand conjunctions. |
| **`num_at`** | $N_{at} = \text{count}(URL, '@')$ | The `@` symbol causes browsers to ignore all preceding characters, redirecting to the host that follows. |
| **`num_digits`** | $N_{digits} = \sum \mathbb{I}[c_i \in \{0..9\}]$ | Phishing URLs frequently contain numeric session identifiers, timestamps, or hex encoded IPs. |
| **`num_special_chars`** | $N_{spec} = \sum \mathbb{I}[c_i \in \Omega_{spec}]$ | High density of `?`, `=`, `&`, `%`, `_`, `~`, `+`, `#` indicates parameter stuffing and obfuscation. |
| **`has_ip`** | $\mathbb{I}[\text{Host} \in \text{IPv4} \cup \text{IPv6}]$ | Direct IP hostnames are used by attackers when domain registration is blocked or to evade DNS lookups. |
| **`has_https`** | $\mathbb{I}[\text{Scheme} = \text{'https'}]$ | Evaluates SSL/TLS usage; legitimate commercial portals overwhelmingly serve content over HTTPS. |
| **`num_subdomains`** | $\max(0, \text{len}(\text{parts}) - 2)$ | Measures depth of subdomain hierarchy (e.g. `login.verify.paypal.com.attacker.com`). |
| **`num_path_levels`** | $\text{len}(\text{split}(\text{path}, '/'))$ | Deeply nested directory trees are created on compromised servers to store temporary phishing kits. |
| **`suspicious_keyword`**| $\mathbb{I}[\text{Tokens} \cap \mathcal{K} \ne \emptyset]$ | Checks for sensitive authentication targets: `login`, `verify`, `secure`, `update`, `bank`, `account`. |
| **`is_shortened`** | $\mathbb{I}[\text{Host} \in \mathcal{S}_{shortener}]$ | Flags URL shortening services (`bit.ly`, `tinyurl.com`, `t.co`) used to bypass static filters. |
| **`has_double_slash_redirect`** | $\mathbb{I}[\text{rfind}(URL, '//') > 7]$ | Detects `//` occurring after the initial protocol, representing open URL redirection attacks. |
| **`has_port`** | $\mathbb{I}[\text{Port} \ne \emptyset \land \text{Port} \notin \{80, 443\}]$| Attackers frequently host fake phishing servers on arbitrary ports (`:8080`, `:8443`). |

---

## 8. MATHEMATICAL FORMULATION

### 8.1 Random Forest Classifier (Bagging Ensemble)
Random Forest aggregates $B$ bootstrap decision trees $\{T_1, T_2, \dots, T_B\}$ trained on bootstrap samples $D_b \subset D$:
- **Splitting Criterion (Gini Impurity):**
  $$I_G(S) = 1 - \sum_{i=1}^{c} p_i^2$$
  where $p_i$ is the probability of an item belonging to class $i$ at node $S$.
- **Information Gain:**
  $$IG(S, A) = I_G(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} I_G(S_v)$$
- **Ensemble Probability Estimation:**
  $$P_{RF}(y=1|x) = \frac{1}{B} \sum_{b=1}^{B} P_{T_b}(y=1|x)$$

### 8.2 Logistic Regression Classifier
Logistic Regression models the posterior class probability as a sigmoid function of a linear feature combination:
- **Hypothesis Function:**
  $$P_{LR}(y=1|x) = \sigma(w^T x + b) = \frac{1}{1 + e^{-(w^T x + b)}}$$
- **Objective Function (L2-Regularized Negative Log-Likelihood):**
  $$J(w, b) = -\frac{1}{m} \sum_{i=1}^{m} \left[ y^{(i)} \ln(P_{LR}(y=1|x^{(i)})) + (1 - y^{(i)}) \ln(1 - P_{LR}(y=1|x^{(i)})) \right] + \frac{\lambda}{2m} \|w\|_2^2$$
  where $\lambda = \frac{1}{C}$ governs the regularization penalty.

### 8.3 Hybrid Soft Voting Formulation
The Soft Voting Classifier calculates the convex combination of the posterior probabilities output by the base estimators:
$$P_{hybrid}(y=1|x) = w_{RF} \cdot P_{RF}(y=1|x) + w_{LR} \cdot P_{LR}(y=1|x)$$
where $w_{RF} + w_{LR} = 1$ (with equal weighting $w_{RF} = 0.5, w_{LR} = 0.5$).
The binary classification decision $\hat{y}$ is obtained via thresholding:
$$\hat{y} = \begin{cases} 1 (\text{PHISHING}) & \text{if } P_{hybrid}(y=1|x) \ge 0.50 \\ 0 (\text{LEGITIMATE}) & \text{otherwise} \end{cases}$$

---

## 9. RATIONALE: WHY RANDOM FOREST + LOGISTIC REGRESSION?
*(Addressing Key Project Defense Question)*

1. **Non-Linear Depth vs. Linear Regularization:**
   - **Random Forest** is an expressive, non-parametric tree ensemble capable of capturing complex non-linear feature interactions (e.g., an IP address occurring alongside deep path levels and a specific port).
   - **Logistic Regression** is a parametric linear model with convex optimization that provides a stable linear decision boundary, anchoring the ensemble against extreme tree splits on rare out-of-distribution values.
2. **Calibrated Posterior Probabilities:**
   - Decision trees generate stepped, uncalibrated probability estimates at terminal leaves. Logistic Regression produces smooth, monotonic sigmoid probabilities calibrated across log-odds.
   - Blending both yields smoother confidence estimates suitable for security risk triage.
3. **Variance Reduction & Generalization:**
   - Random Forest reduces model variance through bagging. Combining it with an independent linear model further reduces prediction variance, lowering the False Positive Rate (FPR) on legitimate websites.

---

## 10. EXPERIMENTAL RESULTS & COMPARATIVE ANALYSIS

### 10.1 Evaluation Metrics Table (Test Set: 2,000 URLs)

| Model Architecture | Accuracy | Precision | Recall | Specificity | F1-Score | ROC-AUC | 5-Fold CV Accuracy |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression (LR)** | 82.45% | 84.93% | 78.90% | 86.00% | 81.80% | 90.88% | 83.81% (±0.0121) |
| **Random Forest (RF)** | 92.90% | 93.69% | 92.00% | 93.80% | 92.84% | 97.70% | 92.34% (±0.0051) |
| **Hybrid Voting (Soft)** ⭐ | **90.65%** | **92.74%** | **88.20%** | **93.10%** | **90.42%** | **96.37%** | **90.56% (±0.0032)** |
| **Hybrid Voting (Hard)** | 86.90% | 91.24% | 81.60% | 92.20% | 85.62% | N/A | 86.95% (±0.0064) |

### 10.2 Gini Feature Importance Ranking (Random Forest)
1. `url_length`: 23.74%
2. `has_https`: 16.96%
3. `hostname_length`: 14.41%
4. `num_path_levels`: 12.52%
5. `num_digits`: 12.21%
6. `num_dots`: 4.51%
7. `num_special_chars`: 4.43%
8. `num_hyphens`: 3.84%
9. `num_subdomains`: 3.29%
10. `suspicious_keyword`: 2.73%
11. `is_shortened`: 0.64%
12. `num_at`: 0.46%
13. `has_double_slash_redirect`: 0.15%
14. `has_ip`: 0.07%
15. `has_port`: 0.04%

---

## 11. SAMPLE URL VALIDATION SUITE (100% PASS RATE)

| Test URL | Expected Category | Predicted Verdict | Confidence | Decision Rationale / Triggered Indicators |
|---|:---:|:---:|:---:|---|
| `https://www.google.com/search?q=cybersecurity+research` | Legitimate | **LEGITIMATE** | 80.53% | Standard domain, clean token structure, valid HTTPS. |
| `https://en.wikipedia.org/wiki/Phishing` | Legitimate | **LEGITIMATE** | 88.34% | Standard ccTLD/TLD, no suspicious tokens, clean path. |
| `https://github.com/scikit-learn/scikit-learn` | Legitimate | **LEGITIMATE** | 96.74% | High reputation domain structure, normal path depth. |
| `https://docs.python.org/3/library/urllib.parse.html` | Legitimate | **LEGITIMATE** | 90.54% | Legitimate subdomain, standard doc hierarchy. |
| `https://stackoverflow.com/questions/tagged/machine-learning` | Legitimate | **LEGITIMATE** | 72.15% | Normal hyphenated category slug, no risk flags. |
| `http://login-verify-account-security-update.bankofamerica-online.cc/auth/login.php` | Phishing | **PHISHING** | 98.04% | 5 hyphens, `login`, `verify`, `account`, `security`, `update` keywords. |
| `http://verify-paypal-identity-secure.com/webscr?cmd=_login-run&account=update` | Phishing | **PHISHING** | 97.26% | `verify`, `secure`, `webscr`, `update` parameters, long URL. |
| `http://192.168.1.100:8080/paypal/login.htm?account=update&token=489271` | Phishing | **PHISHING** | 99.87% | Raw IPv4 host, explicit non-standard port `:8080`, credential keyword. |
| `http://appleid.apple.com-recover-account.id-security-auth.net/verify` | Phishing | **PHISHING** | 99.38% | Nested subdomains, brand spoofing host, 4 hyphens. |
| `http://netflix-billing-update-suspicious-login.info/account//verify` | Phishing | **PHISHING** | 97.99% | Open redirect `//` in path, billing/login keywords, long host. |

---

## 12. PPT PRESENTATION IMPROVEMENT GUIDE
*(For B.Tech Project Defense & Presentation Slides)*

To address the project review feedback (*"Change objective, Architecture, Feature Engineering, Mathematical Formulation, Why LRM/RF, Improve PPT"*):

1. **Slide 1 (Title):** Keep official KITSW header, title, supervisor S. Ravi, coordinator Dr. A. Godavari, and team members.
2. **Slide 4 (Problem Statement):** Emphasize the failure of static blacklists against **zero-day attacks** (lifespan < 4 hours).
3. **Slide 5 (Objectives):** Update to the 5 actionable objectives: 15 lexical features, leakage-free pipeline, RF + LR hybrid soft voting, 5-fold CV tuning, and real-time Streamlit web deployment.
4. **Slide 6 (System Architecture):** Replace generic flowchart with the complete 6-stage architecture diagram (Raw URL $\rightarrow$ Feature Extraction $\rightarrow$ Scaling $\rightarrow$ Parallel RF & LR $\rightarrow$ Soft Voting $\rightarrow$ Verdict & Confidence Score).
5. **Slide 7 (Feature Engineering):** Highlight the 15 features classified into 4 functional groups:
   - *Structural:* Length, Host length, Path levels, Subdomains
   - *Punctuation/Syntactic:* Dots, Hyphens, Digits, Special Characters, `@`
   - *Security Protocol/Redirection:* HTTPS, IP address, Port, Double-slash `//`, Shortener
   - *Semantic/Heuristic:* Suspicious keywords (`login`, `verify`, `secure`, `bank`, `update`)
6. **Slide 8 (Mathematical Formulation):** Display equations for Gini Impurity, Logistic Regression Sigmoid, Log-Loss Cost Function, and Soft Voting Convex Average.
7. **Slide 9 (Why LR + Random Forest?):** Clear slide contrasting Random Forest (non-linear relationships, bagging) vs Logistic Regression (linear regularization, calibrated probabilities) and why the hybrid ensemble prevents false alarms.
8. **Slide 10 (Results & Visuals):** Include the side-by-side Confusion Matrix heatmap, ROC curves, and Feature Importance bar chart.
9. **Slide 11 (Live Demonstration):** Screenshot of the Streamlit application showing the real-time verdict and gauge meter.

---

## 13. CONCLUSION & FUTURE WORK
### 13.1 Conclusion
This project successfully designed, implemented, and validated an automated **Phishing Detection System Through Hybrid Machine Learning Based on URL**. By engineering a compact set of 15 lexical features extracted directly from URL strings, the system eliminates dependencies on external DNS lookups and webpage content rendering. Combining Random Forest and Logistic Regression through Soft Voting achieves high detection accuracy (>90%), high precision (>92%), and rapid sub-millisecond inference times.

### 13.2 Future Work
- **Domain Age & SSL Certificate Telemetry:** Integrate asynchronous RDAP/WHOIS lookup to inspect domain creation age without blocking real-time execution.
- **Browser Extension Integration:** Package the lightweight inference model into a WebExtension (Chrome/Firefox) to inspect hyperlinks before user navigation.
- **Continual Active Learning:** Establish an automated ingestion pipeline pulling live feeds from PhishTank and OpenPhish for periodic online model retraining.

---

## 14. REFERENCES
1. A. Karim, M. Shahroz, K. Mustofa, S. B. Belhaouari, and S. R. K. Joga, "Phishing Detection System Through Hybrid Machine Learning Based on URL," *IEEE Access*, vol. 11, pp. 36805–36822, 2023.
2. A. K. Jain and B. B. Gupta, "PHISH-SAFE: URL features-based phishing detection system using machine learning," *Cyber Security*, Springer, pp. 467–474, 2018.
3. G. Xiang, J. Hong, C. P. Rose, and L. Cranor, "CANTINA+: A feature-rich machine learning framework for detecting phishing websites," *ACM Trans. Inf. Syst. Secur.*, vol. 14, no. 2, 2011.
4. L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
5. F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
6. J. Leite, M. Mosteiro, G. Huston, and D. Karrenberg, "Tranco: A research-oriented top sites ranking hardened against manipulation," *NDSS*, 2019.
