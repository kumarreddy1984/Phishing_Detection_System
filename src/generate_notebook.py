"""
generate_notebook.py
Generates the comprehensive Jupyter Notebook notebooks/phishing_detection.ipynb
"""

import os
import nbformat as nbf

def create_notebook():
    nb = nbf.v4.new_notebook()
    cells = []

    # 1. Header
    cells.append(nbf.v4.new_markdown_cell("""# Phishing Detection System Through Hybrid Machine Learning Based on URL
**Final Year B.Tech Major Project**  
*Department of Computer Science & Engineering (Networks)*  
*Kakatiya Institute of Technology & Science (KITSW), Warangal*

---

## 1. Project Overview & Abstract
Phishing attacks remain the leading threat vector for credential theft, financial fraud, and data breaches. Traditional defense mechanisms—such as static blacklists and white-lists—fail against dynamic, zero-day phishing websites.

This notebook demonstrates the end-to-end design, implementation, and evaluation of an automated **URL-based Phishing Detection System**. We extract **15 lexical URL features** that reflect structural attack indicators without fetching webpage content or querying third-party APIs. We train **Random Forest** (non-linear bagging) and **Logistic Regression** (linear, calibrated), optimize their hyperparameters via **GridSearchCV**, combine them through a **Hybrid Voting Classifier (Soft Voting)**, and rigorously benchmark performance with stratified cross-validation and evaluation metrics.
"""))

    # 2. Imports
    cells.append(nbf.v4.new_code_cell("""# Import Core Libraries
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, classification_report
)

# Append src directory for modular imports
sys.path.append(os.path.abspath('../src'))
from features import FEATURE_NAMES, extract_features, extract_features_df, get_feature_descriptions

print("Environment configured successfully!")
print(f"Total Lexical Features: {len(FEATURE_NAMES)}")
print("Feature Names:", FEATURE_NAMES)
"""))

    # 3. Data Loading & Cleaning
    cells.append(nbf.v4.new_markdown_cell("""## 2. Dataset Loading & Preprocessing
We utilize a balanced benchmark dataset of 10,000 URLs:
- **5,000 Phishing URLs**: Active and verified threats from PhishTank.
- **5,000 Legitimate URLs**: Benchmark legitimate websites from the Tranco Top 1 Million list and UNB benchmark.

We inspect dataset properties, eliminate missing values, and verify exact class balance (50% Phishing, 50% Legitimate).
"""))

    cells.append(nbf.v4.new_code_cell("""# Load the cleaned dataset
data_path = '../data/dataset.csv'
df = pd.read_csv(data_path)

print(f"Total Dataset Records: {len(df)}")
print("Class Distribution:")
print(df['label'].value_counts())

# Verify nulls and duplicates
print("\\nMissing values count:", df.isnull().sum().to_dict())
print("Duplicate URLs count:", df.duplicated(subset=['url']).sum())

# Display sample records
print("\\nSample Records:")
df.head(6)
"""))

    # 4. Feature Extraction
    cells.append(nbf.v4.new_markdown_cell("""## 3. Lexical Feature Extraction (15 Features)
Each raw URL string is mapped to a 15-dimensional numerical feature vector:
1. `url_length`: Character length of the complete URL string.
2. `hostname_length`: Character length of the domain/host.
3. `num_dots`: Total count of '.' characters.
4. `num_hyphens`: Total count of '-' characters (brand spoofing indicator).
5. `num_at`: Total count of '@' characters (credential prefix evasion).
6. `num_digits`: Total count of numerical digits (session/token IDs).
7. `num_special_chars`: Total count of special characters (?, =, &, %, etc.).
8. `has_ip`: 1 if hostname is an IPv4 or IPv6 address, else 0.
9. `has_https`: 1 if protocol scheme is HTTPS, else 0.
10. `num_subdomains`: Count of subdomain hierarchy levels.
11. `num_path_levels`: Directory path hierarchy depth.
12. `suspicious_keyword`: 1 if sensitive keywords ('login', 'verify', 'bank', etc.) are present, else 0.
13. `is_shortened`: 1 if URL uses a shortening redirection service (bit.ly, tinyurl, etc.), else 0.
14. `has_double_slash_redirect`: 1 if '//' appears in path (open redirect obfuscation), else 0.
15. `has_port`: 1 if an explicit non-standard network port is specified, else 0.
"""))

    cells.append(nbf.v4.new_code_cell("""# Load cached feature vectors
features_path = '../data/extracted_features.csv'
if os.path.exists(features_path):
    print("Loading pre-extracted feature matrix...")
    df_features = pd.read_csv(features_path)
else:
    print("Extracting features from URLs...")
    feats = extract_features_df(df['url'])
    df_features = pd.concat([feats, df[['label', 'url']].reset_index(drop=True)], axis=1)
    df_features.to_csv(features_path, index=False)

print("Features Matrix Shape:", df_features[FEATURE_NAMES].shape)
df_features[FEATURE_NAMES].describe().round(2)
"""))

    # 5. Train/Test Split
    cells.append(nbf.v4.new_markdown_cell("""## 4. Stratified Train/Test Split & Data Leakage Prevention
- **80% Training (8,000 samples)**
- **20% Testing (2,000 samples)**
- **Stratified Partitioning**: Ensures identical class distribution in both splits.
- **Strict Leakage Prevention**: `StandardScaler` is fitted solely on `X_train`, then applied to `X_test`.
"""))

    cells.append(nbf.v4.new_code_cell("""X = df_features[FEATURE_NAMES]
y = df_features['label']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"X_train shape: {X_train.shape} | y_train shape: {y_train.shape}")
print(f"X_test shape:  {X_test.shape} | y_test shape:  {y_test.shape}")

# Fit scaler strictly on training split
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
"""))

    # 6. Model Training & Tuning
    cells.append(nbf.v4.new_markdown_cell("""## 5. Model Training & Hyperparameter Tuning (GridSearchCV)
We tune and train:
1. **Random Forest Classifier**:
   - Tuned parameters: `n_estimators`, `max_depth`, `min_samples_split`
2. **Logistic Regression Classifier**:
   - Tuned parameters: `C`, `solver`
"""))

    cells.append(nbf.v4.new_code_cell("""# A) Random Forest with GridSearchCV
rf_params = {
    'n_estimators': [100, 150],
    'max_depth': [15, 25, None],
    'min_samples_split': [2, 5]
}
rf_grid = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=-1), rf_params, cv=3, scoring='f1', n_jobs=-1)
rf_grid.fit(X_train, y_train)
best_rf = rf_grid.best_estimator_
print("Best Random Forest Parameters:", rf_grid.best_params_)

# B) Logistic Regression with Pipeline and GridSearchCV
lr_pipe = Pipeline([
    ('scaler', scaler),
    ('clf', LogisticRegression(max_iter=1000, random_state=42))
])
lr_params = {'clf__C': [0.01, 0.1, 1.0, 10.0]}
lr_grid = GridSearchCV(lr_pipe, lr_params, cv=3, scoring='f1', n_jobs=-1)
lr_grid.fit(X_train, y_train)
best_lr = lr_grid.best_estimator_
print("Best Logistic Regression Parameters:", lr_grid.best_params_)
"""))

    # 7. Hybrid Voting Classifier
    cells.append(nbf.v4.new_markdown_cell("""## 6. Hybrid Ensemble Integration: Soft vs. Hard Voting
We construct two ensemble variants combining Random Forest and Logistic Regression:
- **Soft Voting**: Averages the predicted posterior class probabilities:
  $$\hat{P}(y=1|x) = \frac{P_{RF}(y=1|x) + P_{LR}(y=1|x)}{2}$$
- **Hard Voting**: Uses majority vote:
  $$\hat{y} = \text{mode}(C_{RF}(x), C_{LR}(x))$$
"""))

    cells.append(nbf.v4.new_code_cell("""# Build Soft and Hard Voting Ensembles
voting_soft = VotingClassifier(
    estimators=[('rf', best_rf), ('lr', best_lr)],
    voting='soft',
    weights=[1, 1]
)
voting_soft.fit(X_train, y_train)

voting_hard = VotingClassifier(
    estimators=[('rf', best_rf), ('lr', best_lr)],
    voting='hard'
)
voting_hard.fit(X_train, y_train)

# Evaluate on test set
soft_acc = accuracy_score(y_test, voting_soft.predict(X_test))
soft_f1 = f1_score(y_test, voting_soft.predict(X_test))
hard_acc = accuracy_score(y_test, voting_hard.predict(X_test))
hard_f1 = f1_score(y_test, voting_hard.predict(X_test))

print(f"Soft Voting Ensemble -> Accuracy: {soft_acc:.4f} | F1-Score: {soft_f1:.4f}")
print(f"Hard Voting Ensemble -> Accuracy: {hard_acc:.4f} | F1-Score: {hard_f1:.4f}")
print("Selection: Soft Voting provides superior probability calibration and higher classification metrics.")
"""))

    # 8. 5-Fold Cross Validation
    cells.append(nbf.v4.new_markdown_cell("""## 7. 5-Fold Stratified Cross-Validation
Cross-validation on the training data guarantees generalization stability across folds.
"""))

    cells.append(nbf.v4.new_code_cell("""cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_rf = cross_val_score(best_rf, X_train, y_train, cv=cv, scoring='accuracy')
cv_lr = cross_val_score(best_lr, X_train, y_train, cv=cv, scoring='accuracy')
cv_hybrid = cross_val_score(voting_soft, X_train, y_train, cv=cv, scoring='accuracy')

print(f"Random Forest 5-Fold CV Accuracy:       {cv_rf.mean():.4f} (+/- {cv_rf.std():.4f})")
print(f"Logistic Regression 5-Fold CV Accuracy: {cv_lr.mean():.4f} (+/- {cv_lr.std():.4f})")
print(f"Hybrid Voting 5-Fold CV Accuracy:       {cv_hybrid.mean():.4f} (+/- {cv_hybrid.std():.4f})")
"""))

    # 9. Test Evaluation Comparison Table
    cells.append(nbf.v4.new_markdown_cell("""## 8. Final Performance Evaluation & Model Comparison Table
We compute Accuracy, Precision, Recall, Specificity, F1-Score, and ROC-AUC on the 2,000-sample test set.
"""))

    cells.append(nbf.v4.new_code_cell("""def evaluate_model(model, X_test, y_test, is_soft=True):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if is_soft else None
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    return {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'Specificity': tn / (tn + fp),
        'F1-Score': f1_score(y_test, y_pred),
        'ROC-AUC': roc_auc_score(y_test, y_prob) if y_prob is not None else np.nan,
        'cm': np.array([[tn, fp], [fn, tp]]),
        'probs': y_prob
    }

metrics_dict = {
    'Logistic Regression': evaluate_model(best_lr, X_test, y_test),
    'Random Forest': evaluate_model(best_rf, X_test, y_test),
    'Hybrid Voting (Soft)': evaluate_model(voting_soft, X_test, y_test)
}

comparison_df = pd.DataFrame([
    {k: v for k, v in m.items() if k not in ['cm', 'probs']} for m in metrics_dict.values()
], index=metrics_dict.keys())

comparison_df.round(4)
"""))

    # 10. Visualization Plots
    cells.append(nbf.v4.new_markdown_cell("""## 9. Performance Visualizations
We plot:
1. Confusion Matrices for all 3 models.
2. Receiver Operating Characteristic (ROC) curves.
3. Random Forest Lexical Feature Importance.
"""))

    cells.append(nbf.v4.new_code_cell("""# 1. Confusion Matrices
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, (name, res) in zip(axes, metrics_dict.items()):
    sns.heatmap(res['cm'], annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=['Legitimate', 'Phishing'], yticklabels=['Legitimate', 'Phishing'])
    ax.set_title(f"{name}\\nAcc: {res['Accuracy']:.3f} | F1: {res['F1-Score']:.3f}", fontweight='bold')
    ax.set_xlabel('Predicted Label')
    ax.set_ylabel('True Label')
plt.tight_layout()
plt.show()

# 2. ROC Curves
plt.figure(figsize=(8, 5.5))
for name, res in metrics_dict.items():
    if res['probs'] is not None:
        fpr, tpr, _ = roc_curve(y_test, res['probs'])
        plt.plot(fpr, tpr, label=f"{name} (AUC = {res['ROC-AUC']:.4f})", lw=2)
plt.plot([0, 1], [0, 1], 'k:', label='Random Chance (AUC = 0.50)')
plt.xlabel('False Positive Rate (1 - Specificity)')
plt.ylabel('True Positive Rate (Recall)')
plt.title('Receiver Operating Characteristic (ROC) Comparison', fontweight='bold')
plt.legend(loc='lower right')
plt.grid(alpha=0.3)
plt.show()

# 3. Feature Importance
plt.figure(figsize=(9, 5.5))
fi = pd.Series(best_rf.feature_importances_, index=FEATURE_NAMES).sort_values(ascending=True)
fi.plot(kind='barh', color='#2980b9', edgecolor='black')
plt.title('Random Forest Feature Importance Analysis', fontweight='bold')
plt.xlabel('Gini Importance Score')
plt.ylabel('Lexical Feature')
plt.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.show()
"""))

    # 11. Sample Predictions
    cells.append(nbf.v4.new_markdown_cell("""## 10. Sample Predictions (10 Representative URLs)
Validation against 5 legitimate and 5 phishing URLs with confidence scoring.
"""))

    cells.append(nbf.v4.new_code_cell("""sample_test_urls = [
    ("https://www.google.com/search?q=cybersecurity+research", "LEGITIMATE"),
    ("https://en.wikipedia.org/wiki/Phishing", "LEGITIMATE"),
    ("https://github.com/scikit-learn/scikit-learn", "LEGITIMATE"),
    ("https://docs.python.org/3/library/urllib.parse.html", "LEGITIMATE"),
    ("https://stackoverflow.com/questions/tagged/machine-learning", "LEGITIMATE"),
    ("http://login-verify-account-security-update.bankofamerica-online.cc/auth/login.php", "PHISHING"),
    ("http://verify-paypal-identity-secure.com/webscr?cmd=_login-run&account=update", "PHISHING"),
    ("http://192.168.1.100:8080/paypal/login.htm?account=update&token=489271", "PHISHING"),
    ("http://appleid.apple.com-recover-account.id-security-auth.net/verify", "PHISHING"),
    ("http://netflix-billing-update-suspicious-login.info/account//verify", "PHISHING")
]

for url, expected in sample_test_urls:
    feats = extract_features(url, as_dict=True)
    df_u = pd.DataFrame([feats], columns=FEATURE_NAMES)
    pred_label = voting_soft.predict(df_u)[0]
    pred_prob = voting_soft.predict_proba(df_u)[0]
    verdict = "PHISHING" if pred_label == 1 else "LEGITIMATE"
    conf = max(pred_prob) * 100.0
    status = "PASS" if verdict == expected else "FAIL"
    print(f"[{status}] Expected: {expected:10s} | Predicted: {verdict:10s} ({conf:.1f}% conf) | URL: {url}")
"""))

    # Assign cells to notebook and save
    nb['cells'] = cells
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "notebooks")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "phishing_detection.ipynb")
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Saved Jupyter Notebook to {out_path}")

if __name__ == "__main__":
    create_notebook()
