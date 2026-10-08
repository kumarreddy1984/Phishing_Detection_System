"""
train.py
End-to-end training and evaluation pipeline for Phishing Detection System.
Trains:
1. Random Forest Classifier
2. Logistic Regression Classifier (with StandardScaler)
3. Hybrid Voting Classifier (Soft vs. Hard voting comparison)
Performs Stratified 80/20 split, 5-Fold Cross Validation, GridSearchCV tuning,
evaluates Accuracy, Precision, Recall, Specificity, F1-Score, ROC-AUC,
extracts feature importance, and generates evaluation plots.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve
)

from features import FEATURE_NAMES, extract_features_df

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
EXTRACTED_DATA_PATH = os.path.join(BASE_DIR, "data", "extracted_features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_and_prepare_data(csv_path: str = DATA_PATH):
    """
    Load dataset from CSV, remove duplicates and nulls, and extract features.
    """
    print(f"[*] Loading data from: {csv_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run download_data.py first.")

    df = pd.read_csv(csv_path)
    initial_len = len(df)
    print(f"    Initial records: {initial_len}")

    # Drop nulls and duplicates
    df.dropna(subset=["url", "label"], inplace=True)
    df.drop_duplicates(subset=["url"], inplace=True)
    df["label"] = df["label"].astype(int)
    print(f"    After cleaning: {len(df)} records")

    # Check class balance
    counts = df["label"].value_counts().to_dict()
    print(f"    Class balance: {counts} (0: Legitimate, 1: Phishing)")

    # Extract 15 lexical features if not already cached
    if os.path.exists(EXTRACTED_DATA_PATH):
        print(f"[*] Found cached extracted features at: {EXTRACTED_DATA_PATH}")
        df_features = pd.read_csv(EXTRACTED_DATA_PATH)
        if len(df_features) != len(df) or not all(c in df_features.columns for c in FEATURE_NAMES + ["label"]):
            print("    Cache mismatch. Re-extracting features...")
            df_feats = extract_features_df(df["url"])
            df_features = pd.concat([df_feats, df[["label", "url"]].reset_index(drop=True)], axis=1)
            df_features.to_csv(EXTRACTED_DATA_PATH, index=False)
    else:
        print("[*] Extracting 15 lexical features from raw URLs (this may take a moment)...")
        df_feats = extract_features_df(df["url"])
        df_features = pd.concat([df_feats, df[["label", "url"]].reset_index(drop=True)], axis=1)
        df_features.to_csv(EXTRACTED_DATA_PATH, index=False)
        print(f"[OK] Extracted features saved to {EXTRACTED_DATA_PATH}")

    X = df_features[FEATURE_NAMES]
    y = df_features["label"]
    return X, y, df_features


def calculate_metrics(y_true, y_pred, y_prob=None):
    """
    Calculate Accuracy, Precision, Recall, Specificity, F1-Score, and ROC-AUC.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    f1 = f1_score(y_true, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_true, y_prob) if y_prob is not None else 0.0

    return {
        "Accuracy": float(acc),
        "Precision": float(prec),
        "Recall": float(rec),
        "Specificity": float(spec),
        "F1-Score": float(f1),
        "ROC-AUC": float(roc_auc),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "TP": int(tp)
    }


def train_and_evaluate():
    # 1. Load and prepare dataset
    X, y, df_full = load_and_prepare_data()

    # 2. Stratified 80/20 train/test split
    print("\n[*] Splitting dataset (80% train, 20% test, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"    Train size: {X_train.shape[0]} samples")
    print(f"    Test size:  {X_test.shape[0]} samples")

    # 3. Fit StandardScaler on X_train ONLY to prevent data leakage
    print("\n[*] Fitting StandardScaler on training data...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Hyperparameter tuning & Cross Validation
    print("\n[*] Hyperparameter Tuning & Training Base Models...")

    # A) Random Forest Classifier Tuning
    print("    -> Tuning Random Forest with GridSearchCV...")
    rf_param_grid = {
        "n_estimators": [100, 150],
        "max_depth": [15, 25, None],
        "min_samples_split": [2, 5]
    }
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        rf_param_grid,
        cv=3,
        scoring="f1",
        n_jobs=-1
    )
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_
    print(f"    [+] Best RF Parameters: {rf_grid.best_params_}")

    # B) Logistic Regression Tuning
    print("    -> Tuning Logistic Regression with GridSearchCV...")
    lr_param_grid = {
        "C": [0.01, 0.1, 1.0, 10.0],
        "solver": ["lbfgs"]
    }
    lr_grid = GridSearchCV(
        LogisticRegression(max_iter=1000, random_state=42),
        lr_param_grid,
        cv=3,
        scoring="f1",
        n_jobs=-1
    )
    lr_grid.fit(X_train_scaled, y_train)
    best_lr = lr_grid.best_estimator_
    print(f"    [+] Best LR Parameters: {lr_grid.best_params_}")

    # 5. Hybrid Voting Classifiers (Soft vs. Hard Voting)
    print("\n[*] Building Hybrid Ensemble Models (Random Forest + Logistic Regression)...")

    # To combine in VotingClassifier where LR requires scaling and RF does not,
    # we encapsulate LR with its scaler in a Pipeline:
    lr_pipeline = Pipeline([
        ("scaler", scaler),
        ("clf", best_lr)
    ])

    # Soft Voting Classifier (balanced probability averaging)
    voting_soft = VotingClassifier(
        estimators=[("rf", best_rf), ("lr", lr_pipeline)],
        voting="soft",
        weights=[1, 1]  # Equal contribution from non-linear tree ensemble and calibrated linear model
    )
    voting_soft.fit(X_train, y_train)

    # Hard Voting Classifier
    voting_hard = VotingClassifier(
        estimators=[("rf", best_rf), ("lr", lr_pipeline)],
        voting="hard"
    )
    voting_hard.fit(X_train, y_train)

    # Compare Soft vs Hard on Validation / Test
    soft_test_pred = voting_soft.predict(X_test)
    soft_test_prob = voting_soft.predict_proba(X_test)[:, 1]
    hard_test_pred = voting_hard.predict(X_test)

    soft_metrics = calculate_metrics(y_test, soft_test_pred, soft_test_prob)
    hard_metrics = calculate_metrics(y_test, hard_test_pred, None)

    print("\n--- Voting Mechanism Comparison ---")
    print(f"Soft Voting - Accuracy: {soft_metrics['Accuracy']:.4f}, F1: {soft_metrics['F1-Score']:.4f}, ROC-AUC: {soft_metrics['ROC-AUC']:.4f}")
    print(f"Hard Voting - Accuracy: {hard_metrics['Accuracy']:.4f}, F1: {hard_metrics['F1-Score']:.4f}")

    if soft_metrics["F1-Score"] >= hard_metrics["F1-Score"]:
        print("[+] Soft Voting selected as superior hybrid configuration (provides probabilities & higher F1).")
        best_hybrid = voting_soft
        hybrid_type = "soft"
    else:
        print("[+] Hard Voting selected as superior hybrid configuration.")
        best_hybrid = voting_hard
        hybrid_type = "hard"

    # 6. Comprehensive 5-Fold Stratified Cross-Validation on Training Set
    print("\n[*] Performing 5-Fold Stratified Cross-Validation on Training Data...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf_cv_scores = cross_val_score(best_rf, X_train, y_train, cv=cv, scoring="accuracy")
    lr_cv_scores = cross_val_score(lr_pipeline, X_train, y_train, cv=cv, scoring="accuracy")
    hybrid_cv_scores = cross_val_score(best_hybrid, X_train, y_train, cv=cv, scoring="accuracy")

    print(f"    Random Forest 5-Fold CV Accuracy:       {rf_cv_scores.mean():.4f} (+/- {rf_cv_scores.std():.4f})")
    print(f"    Logistic Regression 5-Fold CV Accuracy: {lr_cv_scores.mean():.4f} (+/- {lr_cv_scores.std():.4f})")
    print(f"    Hybrid Voting 5-Fold CV Accuracy:       {hybrid_cv_scores.mean():.4f} (+/- {hybrid_cv_scores.std():.4f})")

    # 7. Test Set Predictions & Evaluation for All Models
    print("\n[*] Evaluating All Models on Test Set (20% hold-out)...")

    # Random Forest
    rf_pred = best_rf.predict(X_test)
    rf_prob = best_rf.predict_proba(X_test)[:, 1]
    rf_metrics = calculate_metrics(y_test, rf_pred, rf_prob)

    # Logistic Regression
    lr_pred = lr_pipeline.predict(X_test)
    lr_prob = lr_pipeline.predict_proba(X_test)[:, 1]
    lr_metrics = calculate_metrics(y_test, lr_pred, lr_prob)

    # Hybrid Model
    hybrid_pred = best_hybrid.predict(X_test)
    hybrid_prob = best_hybrid.predict_proba(X_test)[:, 1] if hybrid_type == "soft" else None
    hybrid_metrics = calculate_metrics(y_test, hybrid_pred, hybrid_prob)

    # Comparison Table
    comparison_df = pd.DataFrame({
        "Model": ["Logistic Regression", "Random Forest", f"Hybrid Voting ({hybrid_type.title()})"],
        "Accuracy": [lr_metrics["Accuracy"], rf_metrics["Accuracy"], hybrid_metrics["Accuracy"]],
        "Precision": [lr_metrics["Precision"], rf_metrics["Precision"], hybrid_metrics["Precision"]],
        "Recall": [lr_metrics["Recall"], rf_metrics["Recall"], hybrid_metrics["Recall"]],
        "Specificity": [lr_metrics["Specificity"], rf_metrics["Specificity"], hybrid_metrics["Specificity"]],
        "F1-Score": [lr_metrics["F1-Score"], rf_metrics["F1-Score"], hybrid_metrics["F1-Score"]],
        "ROC-AUC": [lr_metrics["ROC-AUC"], rf_metrics["ROC-AUC"], hybrid_metrics["ROC-AUC"]]
    })

    print("\n" + "="*75)
    print("                      MODEL EVALUATION COMPARISON TABLE")
    print("="*75)
    print(comparison_df.to_string(index=False))
    print("="*75)

    # 8. Feature Importance from Random Forest
    print("\n[*] Extracting Feature Importance from Random Forest...")
    feat_importances = pd.Series(best_rf.feature_importances_, index=FEATURE_NAMES).sort_values(ascending=False)
    print(feat_importances.to_string())

    # 9. Generate and Save Visualizations
    print("\n[*] Generating evaluation plots...")

    # Plot A: Confusion Matrices
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    models_cm = [
        ("Logistic Regression", lr_metrics),
        ("Random Forest", rf_metrics),
        (f"Hybrid ({hybrid_type.title()} Voting)", hybrid_metrics)
    ]
    for ax, (m_name, m_dict) in zip(axes, models_cm):
        cm = np.array([[m_dict["TN"], m_dict["FP"]], [m_dict["FN"], m_dict["TP"]]])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax,
                    xticklabels=["Legitimate", "Phishing"],
                    yticklabels=["Legitimate", "Phishing"])
        ax.set_title(f"{m_name}\nAcc: {m_dict['Accuracy']:.3f} | F1: {m_dict['F1-Score']:.3f}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Label")

    plt.tight_layout()
    cm_path = os.path.join(REPORTS_DIR, "confusion_matrices.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"    [OK] Saved confusion matrices to: {cm_path}")

    # Plot B: ROC Curves
    plt.figure(figsize=(8, 6))
    fpr_lr, tpr_lr, _ = roc_curve(y_test, lr_prob)
    plt.plot(fpr_lr, tpr_lr, label=f"Logistic Regression (AUC = {lr_metrics['ROC-AUC']:.4f})", color="#2b5c8f", lw=2)

    fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_prob)
    plt.plot(fpr_rf, tpr_rf, label=f"Random Forest (AUC = {rf_metrics['ROC-AUC']:.4f})", color="#27ae60", lw=2)

    if hybrid_prob is not None:
        fpr_hyb, tpr_hyb, _ = roc_curve(y_test, hybrid_prob)
        plt.plot(fpr_hyb, tpr_hyb, label=f"Hybrid Voting (AUC = {hybrid_metrics['ROC-AUC']:.4f})", color="#e74c3c", lw=2.5, linestyle="--")

    plt.plot([0, 1], [0, 1], "k:", lw=1.5, label="Random Chance (AUC = 0.5000)")
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=11)
    plt.ylabel("True Positive Rate (Recall)", fontsize=11)
    plt.title("Receiver Operating Characteristic (ROC) Comparison", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    roc_path = os.path.join(REPORTS_DIR, "roc_curves.png")
    plt.savefig(roc_path, dpi=300)
    plt.close()
    print(f"    [OK] Saved ROC curves to: {roc_path}")

    # Plot C: Feature Importance
    plt.figure(figsize=(10, 6))
    feat_importances.sort_values(ascending=True).plot(kind="barh", color="#2980b9", edgecolor="black")
    plt.title("Random Forest Lexical Feature Importance", fontsize=13, fontweight="bold")
    plt.xlabel("Gini Importance Score", fontsize=11)
    plt.ylabel("Extracted Lexical Feature", fontsize=11)
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    fi_path = os.path.join(REPORTS_DIR, "feature_importance.png")
    plt.savefig(fi_path, dpi=300)
    plt.close()
    print(f"    [OK] Saved feature importance plot to: {fi_path}")

    # Plot D: Metrics Bar Chart Comparison
    plt.figure(figsize=(10, 5))
    metrics_plot_df = comparison_df.melt(id_vars="Model", value_vars=["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"])
    sns.barplot(data=metrics_plot_df, x="variable", y="value", hue="Model", palette=["#3498db", "#2ecc71", "#e74c3c"])
    plt.title("Performance Metric Comparison Across Models", fontsize=13, fontweight="bold")
    plt.xlabel("Metric", fontsize=11)
    plt.ylabel("Score (0.0 - 1.0)", fontsize=11)
    plt.ylim(0.7, 1.02)
    plt.legend(loc="lower right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    mc_path = os.path.join(REPORTS_DIR, "model_comparison.png")
    plt.savefig(mc_path, dpi=300)
    plt.close()
    print(f"    [OK] Saved model comparison plot to: {mc_path}")

    # 10. Save Models, Pipeline, and Metrics with Joblib
    print("\n[*] Saving models and artifacts...")
    joblib.dump(best_hybrid, os.path.join(MODELS_DIR, "hybrid_model.joblib"))
    joblib.dump(best_rf, os.path.join(MODELS_DIR, "random_forest_model.joblib"))
    joblib.dump(best_lr, os.path.join(MODELS_DIR, "logistic_regression_model.joblib"))
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.joblib"))
    joblib.dump(FEATURE_NAMES, os.path.join(MODELS_DIR, "feature_names.joblib"))

    # Save summary dictionary
    summary = {
        "dataset_size": len(df_full),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "best_rf_params": rf_grid.best_params_,
        "best_lr_params": lr_grid.best_params_,
        "hybrid_type": hybrid_type,
        "metrics": {
            "logistic_regression": lr_metrics,
            "random_forest": rf_metrics,
            "hybrid_voting": hybrid_metrics
        },
        "cv_scores": {
            "random_forest": {"mean": float(rf_cv_scores.mean()), "std": float(rf_cv_scores.std())},
            "logistic_regression": {"mean": float(lr_cv_scores.mean()), "std": float(lr_cv_scores.std())},
            "hybrid_voting": {"mean": float(hybrid_cv_scores.mean()), "std": float(hybrid_cv_scores.std())}
        },
        "feature_importance": feat_importances.to_dict()
    }
    with open(os.path.join(MODELS_DIR, "metrics_summary.json"), "w") as f:
        json.dump(summary, f, indent=4)

    print(f"[OK] All models saved to {MODELS_DIR}")
    print("[OK] Training pipeline complete!")
    return summary


if __name__ == "__main__":
    train_and_evaluate()
