"""
features.py
Feature extraction module for the Phishing Detection System.
Extracts 15 lexical URL features defined in the project architecture.
"""

import re
import urllib.parse
from typing import Dict, List, Union, Any
import pandas as pd
import numpy as np

# Ordered list of the 15 features
FEATURE_NAMES = [
    "url_length",
    "hostname_length",
    "num_dots",
    "num_hyphens",
    "num_at",
    "num_digits",
    "num_special_chars",
    "has_ip",
    "has_https",
    "num_subdomains",
    "num_path_levels",
    "suspicious_keyword",
    "is_shortened",
    "has_double_slash_redirect",
    "has_port"
]

# Set of special characters
SPECIAL_CHARS = set("?=&%_~+#$:;!*()[]")

# Suspicious keywords commonly exploited in phishing URLs
SUSPICIOUS_KEYWORDS = {
    "login", "verify", "secure", "update", "bank",
    "account", "banking", "confirm", "signin", "security",
    "webscr", "ebayisapi", "password", "wallet", "authenticate"
}

# Known URL shortener services
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
    "is.gd", "buff.ly", "adf.ly", "bit.do", "tiny.cc",
    "lnkd.in", "db.tt", "qr.ae", "cur.lv", "cutt.ly",
    "rebrand.ly", "shorte.st", "trib.al", "t.ly", "shorturl.at"
}

# Regex to detect IPv4 addresses
IPV4_REGEX = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)

# Regex to detect IPv6 addresses
IPV6_REGEX = re.compile(
    r"^\[?([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}\]?$"
)


def extract_features(url: str, as_dict: bool = True) -> Union[Dict[str, Any], List[Union[int, float]]]:
    """
    Extract 15 lexical URL features from a single raw URL string.

    Parameters
    ----------
    url : str
        The raw uniform resource locator string to inspect.
    as_dict : bool, default=True
        If True, returns a dictionary mapping feature names to extracted values.
        If False, returns a list of values ordered according to FEATURE_NAMES.

    Returns
    -------
    dict or list
        Extracted features for the URL.
    """
    if not isinstance(url, str):
        url = str(url) if url is not None else ""

    url_clean = url.strip()
    url_lower = url_clean.lower()

    # Prepend scheme if missing for robust URL parsing
    parse_target = url_clean
    if not (url_lower.startswith("http://") or url_lower.startswith("https://") or url_lower.startswith("ftp://")):
        parse_target = "http://" + url_clean

    try:
        parsed = urllib.parse.urlparse(parse_target)
        hostname = (parsed.hostname or "").lower()
        netloc = (parsed.netloc or "").lower()
        path = parsed.path or ""
    except Exception:
        hostname = ""
        netloc = ""
        path = ""

    # Feature 1: URL Length
    url_length = len(url_clean)

    # Feature 2: Hostname Length
    hostname_length = len(hostname)

    # Feature 3: Number of Dots
    num_dots = url_clean.count(".")

    # Feature 4: Number of Hyphens
    num_hyphens = url_clean.count("-")

    # Feature 5: Number of '@' symbols
    num_at = url_clean.count("@")

    # Feature 6: Number of numeric digits
    num_digits = sum(1 for c in url_clean if c.isdigit())

    # Feature 7: Number of special characters
    num_special_chars = sum(1 for c in url_clean if c in SPECIAL_CHARS)

    # Feature 8: Presence of an IP address
    # Remove port from netloc/hostname if present
    host_clean = hostname.split(":")[0] if hostname else ""
    has_ip = 1 if (IPV4_REGEX.match(host_clean) or IPV6_REGEX.match(host_clean)) else 0

    # Feature 9: HTTPS usage in scheme
    has_https = 1 if url_lower.startswith("https://") else 0

    # Feature 10: Number of subdomains
    if has_ip or not host_clean:
        num_subdomains = 0
    else:
        # Strip leading 'www.'
        domain_to_split = host_clean[4:] if host_clean.startswith("www.") else host_clean
        parts = [p for p in domain_to_split.split(".") if p]
        # Main domain + TLD = 2 parts, anything beyond is a subdomain level
        num_subdomains = max(0, len(parts) - 2)

    # Feature 11: Number of path levels / depth
    path_clean = path.strip("/")
    if path_clean:
        num_path_levels = len([seg for seg in path_clean.split("/") if seg])
    else:
        num_path_levels = 0

    # Feature 12: Presence of suspicious keywords
    # Checks for sensitive authentication / financial target terms using exact tokens
    url_tokens = set(re.split(r"[^a-zA-Z0-9]+", url_lower))
    suspicious_keyword = 1 if bool(url_tokens.intersection(SUSPICIOUS_KEYWORDS)) else 0

    # Feature 13: URL shortening service usage
    is_shortened = 0
    if host_clean:
        if host_clean in SHORTENER_DOMAINS:
            is_shortened = 1
        elif any(host_clean.endswith("." + sd) for sd in SHORTENER_DOMAINS):
            is_shortened = 1
        elif (len(host_clean) <= 9) and (host_clean.endswith(".ly") or host_clean.endswith(".co") or host_clean.endswith(".to")):
            is_shortened = 1

    # Feature 14: Presence of '//' redirection in path
    # Look for '//' appearing after the initial protocol (beyond index 7)
    has_double_slash_redirect = 1 if (url_clean.rfind("//") > 7) else 0

    # Feature 15: Presence of an explicit port number
    has_port = 0
    try:
        if parsed.port is not None:
            has_port = 1
    except ValueError:
        # Malformed port string in netloc
        has_port = 1

    if not has_port and ":" in netloc:
        port_part = netloc.split(":")[-1]
        if port_part.isdigit():
            has_port = 1

    features_dict = {
        "url_length": int(url_length),
        "hostname_length": int(hostname_length),
        "num_dots": int(num_dots),
        "num_hyphens": int(num_hyphens),
        "num_at": int(num_at),
        "num_digits": int(num_digits),
        "num_special_chars": int(num_special_chars),
        "has_ip": int(has_ip),
        "has_https": int(has_https),
        "num_subdomains": int(num_subdomains),
        "num_path_levels": int(num_path_levels),
        "suspicious_keyword": int(suspicious_keyword),
        "is_shortened": int(is_shortened),
        "has_double_slash_redirect": int(has_double_slash_redirect),
        "has_port": int(has_port)
    }

    if as_dict:
        return features_dict
    return [features_dict[name] for name in FEATURE_NAMES]


def extract_features_df(urls: Union[List[str], pd.Series]) -> pd.DataFrame:
    """
    Extract features for a collection of URLs and return a pandas DataFrame.

    Parameters
    ----------
    urls : list or pd.Series
        Collection of URL strings.

    Returns
    -------
    pd.DataFrame
        DataFrame with 15 columns matching FEATURE_NAMES.
    """
    records = [extract_features(u, as_dict=True) for u in urls]
    return pd.DataFrame(records, columns=FEATURE_NAMES)


def get_feature_descriptions() -> Dict[str, Dict[str, str]]:
    """
    Return metadata and cyber security context for each of the 15 features.
    """
    return {
        "url_length": {
            "name": "URL Length",
            "type": "Numeric",
            "description": "Total character count of the URL. Phishing URLs frequently use elongated paths or tokens to hide destination."
        },
        "hostname_length": {
            "name": "Hostname Length",
            "type": "Numeric",
            "description": "Length of domain/host string. Attackers often craft long hostnames mimicking legitimate brand names."
        },
        "num_dots": {
            "name": "Number of Dots",
            "type": "Numeric",
            "description": "Count of '.' in the URL. Excessive dots are used to construct misleading subdomains."
        },
        "num_hyphens": {
            "name": "Number of Hyphens",
            "type": "Numeric",
            "description": "Count of '-' in the URL. Hyphens are commonly used in typosquatting (e.g., paypal-security.com)."
        },
        "num_at": {
            "name": "Number of '@' Symbols",
            "type": "Numeric",
            "description": "Presence of '@'. Browsers ignore the text preceding '@' and connect to the domain following it."
        },
        "num_digits": {
            "name": "Number of Digits",
            "type": "Numeric",
            "description": "Count of numbers. Phishing links often contain session IDs, timestamps, or randomized hex hashes."
        },
        "num_special_chars": {
            "name": "Number of Special Characters",
            "type": "Numeric",
            "description": "Count of characters like ?, =, &, %, _, ~, +, #. Indicates parameter stuffing and obfuscation."
        },
        "has_ip": {
            "name": "Presence of IP Address",
            "type": "Binary (0/1)",
            "description": "1 if hostname is an IPv4 or IPv6 address. Legitimate brands rarely use direct IP hostnames."
        },
        "has_https": {
            "name": "HTTPS Usage",
            "type": "Binary (0/1)",
            "description": "1 if URL uses HTTPS scheme. Lack of HTTPS or fraudulent SSL usage provides discriminative signal."
        },
        "num_subdomains": {
            "name": "Number of Subdomains",
            "type": "Numeric",
            "description": "Count of subdomain levels beyond root and TLD (e.g. login.update.paypal.com.attacker.com)."
        },
        "num_path_levels": {
            "name": "Path Levels (Depth)",
            "type": "Numeric",
            "description": "Directory depth hierarchy in URL path. Phishing URLs often nest deep directory trees."
        },
        "suspicious_keyword": {
            "name": "Suspicious Keywords",
            "type": "Binary (0/1)",
            "description": "1 if keywords like 'login', 'verify', 'bank', 'secure', 'update' are found in the URL."
        },
        "is_shortened": {
            "name": "URL Shortener Used",
            "type": "Binary (0/1)",
            "description": "1 if known URL shortening service (bit.ly, tinyurl, etc.) is used to mask the destination."
        },
        "has_double_slash_redirect": {
            "name": "Redirection via '//'",
            "type": "Binary (0/1)",
            "description": "1 if '//' appears beyond protocol position, indicating open URL redirection or path evasion."
        },
        "has_port": {
            "name": "Presence of Port Number",
            "type": "Binary (0/1)",
            "description": "1 if non-standard or explicit TCP port is stated in the netloc (e.g. :8080, :8443)."
        }
    }


if __name__ == "__main__":
    test_urls = [
        "https://www.google.com/search?q=machine+learning",
        "http://192.168.1.1:8080/paypal/login/verify.php?account=update&token=82937#secure",
        "http://bit.ly/3xY7z9Q",
        "https://secure-login.bankofamerica.com.account-update.xyz/auth//signin"
    ]
    for u in test_urls:
        print(f"\nURL: {u}")
        feats = extract_features(u)
        for k, v in feats.items():
            print(f"  {k}: {v}")
