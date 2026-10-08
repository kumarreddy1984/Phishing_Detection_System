"""
predict.py
Inference module and CLI prediction tool for the Phishing Detection System.
Loads the trained hybrid voting classifier and extracts the 15 lexical features.
"""

import os
import sys
import argparse
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List

from features import FEATURE_NAMES, extract_features, get_feature_descriptions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "hybrid_model.joblib")
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, "feature_names.joblib")

_model = None
_feature_names = None


def load_model():
    """
    Lazy load the trained model and feature names.
    """
    global _model, _feature_names
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run src/train.py first.")
        _model = joblib.load(MODEL_PATH)
        _feature_names = joblib.load(FEATURE_NAMES_PATH) if os.path.exists(FEATURE_NAMES_PATH) else FEATURE_NAMES
    return _model, _feature_names


def predict_url(url: str) -> Dict[str, Any]:
    """
    Predict whether a given URL is PHISHING or LEGITIMATE.

    Parameters
    ----------
    url : str
        The raw URL string to test.

    Returns
    -------
    dict
        Prediction results including verdict, confidence score,
        phishing probability, legitimate probability, and extracted features.
    """
    model, feature_names = load_model()
    features_dict = extract_features(url, as_dict=True)

    # Format into DataFrame with correct column order
    input_df = pd.DataFrame([features_dict], columns=feature_names)

    # Predict
    raw_pred = model.predict(input_df)[0]

    # Predict probability if soft voting is enabled
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(input_df)[0]
        legit_prob = float(probs[0])
        phish_prob = float(probs[1])
        confidence = float(max(legit_prob, phish_prob) * 100.0)
    else:
        legit_prob = 0.0 if raw_pred == 1 else 1.0
        phish_prob = 1.0 if raw_pred == 1 else 0.0
        confidence = 100.0

    verdict = "PHISHING" if raw_pred == 1 else "LEGITIMATE"

    # Identify notable risk indicators
    risk_flags = []
    if features_dict["has_ip"] == 1:
        risk_flags.append("Host is an IP address instead of a domain name")
    if features_dict["is_shortened"] == 1:
        risk_flags.append("URL uses a known shortening redirection service")
    if features_dict["has_double_slash_redirect"] == 1:
        risk_flags.append("Contains '//' redirection sequence in URL path")
    if features_dict["suspicious_keyword"] == 1:
        risk_flags.append("Contains sensitive authentication/financial keywords")
    if features_dict["num_at"] > 0:
        risk_flags.append("Contains '@' symbol (credential prefix obfuscation)")
    if features_dict["has_port"] == 1:
        risk_flags.append("Explicit non-standard network port specified")
    if features_dict["num_subdomains"] >= 2:
        risk_flags.append(f"Excessive subdomain depth ({features_dict['num_subdomains']} levels)")
    if features_dict["num_hyphens"] >= 3:
        risk_flags.append(f"High hyphen frequency ({features_dict['num_hyphens']} hyphens) mimicking brands")
    if features_dict["url_length"] > 75:
        risk_flags.append(f"Abnormally long URL length ({features_dict['url_length']} characters)")

    return {
        "url": url,
        "prediction": verdict,
        "is_phishing": bool(raw_pred == 1),
        "confidence": round(confidence, 2),
        "phishing_probability": round(phish_prob * 100.0, 2),
        "legitimate_probability": round(legit_prob * 100.0, 2),
        "risk_flags": risk_flags,
        "features": features_dict
    }


def predict_batch(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Run predictions on a list of URLs.
    """
    return [predict_url(u) for u in urls]


def run_sample_tests():
    """
    Test suite containing at least 5 sample phishing and 5 legitimate URLs.
    """
    sample_urls = [
        # 5 Legitimate URLs
        ("https://www.google.com/search?q=cybersecurity+research", "LEGITIMATE"),
        ("https://en.wikipedia.org/wiki/Phishing", "LEGITIMATE"),
        ("https://github.com/scikit-learn/scikit-learn", "LEGITIMATE"),
        ("https://docs.python.org/3/library/urllib.parse.html", "LEGITIMATE"),
        ("https://stackoverflow.com/questions/tagged/machine-learning", "LEGITIMATE"),

        # 5 Phishing URLs
        ("http://login-verify-account-security-update.bankofamerica-online.cc/auth/login.php", "PHISHING"),
        ("http://verify-paypal-identity-secure.com/webscr?cmd=_login-run&account=update", "PHISHING"),
        ("http://192.168.1.100:8080/paypal/login.htm?account=update&token=489271", "PHISHING"),
        ("http://appleid.apple.com-recover-account.id-security-auth.net/verify", "PHISHING"),
        ("http://netflix-billing-update-suspicious-login.info/account//verify", "PHISHING")
    ]

    print("=" * 80)
    print("                PHISHING DETECTION SYSTEM - SAMPLE URL TEST SUITE")
    print("=" * 80)

    correct = 0
    for idx, (url, expected) in enumerate(sample_urls, 1):
        res = predict_url(url)
        is_correct = (res["prediction"] == expected)
        if is_correct:
            correct += 1
        status_marker = "[PASS]" if is_correct else "[FAIL]"

        print(f"\nTest {idx:02d}: {status_marker}")
        print(f"  URL:        {url}")
        print(f"  Expected:   {expected}")
        print(f"  Predicted:  {res['prediction']} (Confidence: {res['confidence']:.2f}%)")
        print(f"  P(Phish):   {res['phishing_probability']:.2f}% | P(Legit): {res['legitimate_probability']:.2f}%")
        if res["risk_flags"]:
            print(f"  Flags:      {', '.join(res['risk_flags'])}")
        else:
            print("  Flags:      None (Clean lexical structure)")

    print("\n" + "=" * 80)
    print(f"Test Summary: {correct} / {len(sample_urls)} Passed ({correct/len(sample_urls)*100.0:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict whether a URL is Phishing or Legitimate.")
    parser.add_argument("--url", type=str, help="Single URL to test.")
    parser.add_argument("--test", action="store_true", help="Run the built-in 10-URL sample test suite.")
    args = parser.parse_args()

    if args.url:
        result = predict_url(args.url)
        print("\n" + "=" * 60)
        print("          URL CLASSIFICATION RESULT")
        print("=" * 60)
        print(f"Target URL:    {result['url']}")
        print(f"Verdict:       {result['prediction']}")
        print(f"Confidence:    {result['confidence']:.2f}%")
        print(f"P(Phishing):   {result['phishing_probability']:.2f}%")
        print(f"P(Legitimate): {result['legitimate_probability']:.2f}%")
        if result["risk_flags"]:
            print("\nIdentified Risk Flags:")
            for flag in result["risk_flags"]:
                print(f"  - {flag}")
        print("\nExtracted Lexical Features (15 Features):")
        for k, v in result["features"].items():
            print(f"  {k:26s}: {v}")
        print("=" * 60)
    else:
        run_sample_tests()
