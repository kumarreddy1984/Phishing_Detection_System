"""
generate_pptx.py
================
Generates two PPTX presentations for the Major Project:
  1. Phishing_Abstract_Presentation.pptx  (12 slides)
  2. Phishing_Execution_Presentation.pptx (17 slides)

Run:
    python src/generate_pptx.py
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

# ── Colour palette ────────────────────────────────────────────────────────────
DARK_BLUE  = RGBColor(0x1B, 0x3A, 0x6B)   # #1B3A6B  – background / header
TEAL       = RGBColor(0x00, 0xB4, 0xD8)   # #00B4D8  – accent
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GREY = RGBColor(0xEC, 0xF0, 0xF1)   # slide body background
MID_GREY   = RGBColor(0xBD, 0xC3, 0xC7)
GOLD       = RGBColor(0xF3, 0x9C, 0x12)   # emphasis

SLIDE_W = Inches(13.33)   # 16:9
SLIDE_H = Inches(7.5)

# ── helpers ───────────────────────────────────────────────────────────────────

def new_prs():
    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def blank_slide(prs):
    """Return a truly blank slide (layout 6)."""
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


def fill_bg(slide, color=LIGHT_GREY):
    """Fill the slide background with a solid colour."""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, l, t, w, h, fill_color, line_color=None, line_width=Pt(0)):
    from pptx.util import Pt
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        l, t, w, h
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape


def add_textbox(slide, text, l, t, w, h,
                font_size=Pt(14), bold=False, italic=False,
                color=DARK_BLUE, align=PP_ALIGN.LEFT,
                wrap=True, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = font_size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox


def header_bar(slide, title_text, subtitle_text=""):
    """Dark-blue top bar with white title text."""
    bar = add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.3), DARK_BLUE)
    # Title
    add_textbox(slide, title_text,
                Inches(0.3), Inches(0.1), Inches(12), Inches(0.75),
                font_size=Pt(26), bold=True, color=WHITE,
                align=PP_ALIGN.LEFT)
    if subtitle_text:
        add_textbox(slide, subtitle_text,
                    Inches(0.3), Inches(0.85), Inches(12), Inches(0.4),
                    font_size=Pt(14), color=TEAL, align=PP_ALIGN.LEFT)


def teal_accent_line(slide, y=Inches(1.3)):
    """Thin teal horizontal rule under the header bar."""
    add_rect(slide, Inches(0), y, SLIDE_W, Pt(4), TEAL)


def slide_number(slide, num, total):
    add_textbox(slide, f"{num} / {total}",
                Inches(11.8), Inches(7.1), Inches(1.5), Inches(0.35),
                font_size=Pt(10), color=MID_GREY, align=PP_ALIGN.RIGHT)


def add_notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def bullet_box(slide, bullets, l=Inches(0.4), t=Inches(1.45),
               w=Inches(12.5), h=Inches(5.6),
               font_size=Pt(15), color=DARK_BLUE, spacing=Pt(6)):
    """
    bullets: list of str or (str, int) where int = indent level (0=top).
    """
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    for item in bullets:
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0

        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        p.level = level
        p.space_before = spacing
        run = p.add_run()
        run.text = ("    " * level) + ("• " if level == 0 else "  – ") + text
        run.font.size = font_size
        run.font.color.rgb = color
        run.font.name = "Calibri"

    return txBox


def add_table(slide, headers, rows,
              l=Inches(0.4), t=Inches(1.5),
              w=Inches(12.5), h=Inches(5.2),
              header_fill=DARK_BLUE, header_color=WHITE,
              row_fill_alt=RGBColor(0xD6, 0xEA, 0xF8),
              font_size=Pt(11)):
    from pptx.util import Pt
    cols = len(headers)
    total_rows = 1 + len(rows)
    tbl = slide.shapes.add_table(total_rows, cols, l, t, w, h).table

    col_width = w // cols
    for i in range(cols):
        tbl.columns[i].width = col_width

    # Header row
    for ci, hdr in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = hdr
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_fill
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0]
        run.font.bold = True
        run.font.size = font_size
        run.font.color.rgb = header_color
        run.font.name = "Calibri"

    # Data rows
    for ri, row in enumerate(rows):
        fill = row_fill_alt if ri % 2 == 0 else WHITE
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = fill
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.runs[0]
            run.font.size = font_size
            run.font.name = "Calibri"
            run.font.color.rgb = DARK_BLUE

    return tbl


# ══════════════════════════════════════════════════════════════════════════════
# DECK 1 – ABSTRACT PRESENTATION  (12 slides)
# ══════════════════════════════════════════════════════════════════════════════

def build_abstract_deck():
    prs = new_prs()
    TOTAL = 13  # total slide count

    # ── Slide 1: Title ────────────────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, DARK_BLUE)
    # Decorative teal band
    add_rect(s, Inches(0), Inches(4.8), SLIDE_W, Inches(0.08), TEAL)
    add_rect(s, Inches(0), Inches(6.5), SLIDE_W, Inches(0.08), TEAL)

    add_textbox(s, "Phishing Detection System",
                Inches(0.5), Inches(0.9), Inches(12.3), Inches(0.9),
                font_size=Pt(34), bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_textbox(s, "Through Hybrid Machine Learning Based on URL",
                Inches(0.5), Inches(1.7), Inches(12.3), Inches(0.7),
                font_size=Pt(24), bold=False, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, "Abstract / Proposal Presentation",
                Inches(0.5), Inches(2.55), Inches(12.3), Inches(0.5),
                font_size=Pt(16), italic=True, color=LIGHT_GREY, align=PP_ALIGN.CENTER)
    add_rect(s, Inches(1.5), Inches(3.2), Inches(10.3), Pt(1.5), TEAL)

    add_textbox(s, "Team Members:",
                Inches(0.6), Inches(3.4), Inches(6), Inches(0.35),
                font_size=Pt(13), bold=True, color=TEAL)
    members = ("Pasula Udaya  |  Sadiya Masarrath  |  Pulugu Kumar Reddy\n"
               "Sampangi Nithin  |  Penchala Hansika")
    add_textbox(s, members,
                Inches(0.6), Inches(3.75), Inches(12), Inches(0.7),
                font_size=Pt(13), color=WHITE, align=PP_ALIGN.LEFT)

    add_textbox(s, "Supervisor: S. Ravi  |  Coordinator: Dr. A. Godavari",
                Inches(0.6), Inches(4.55), Inches(12), Inches(0.4),
                font_size=Pt(12), color=LIGHT_GREY)
    add_textbox(s, "Dept. of CSE (Networks)  |  Kakatiya Institute of Technology & Science (KITSW), Warangal",
                Inches(0.6), Inches(4.95), Inches(12), Inches(0.4),
                font_size=Pt(12), color=LIGHT_GREY)
    add_textbox(s, "Academic Year: 2025-2026",
                Inches(0.6), Inches(5.35), Inches(12), Inches(0.4),
                font_size=Pt(12), color=LIGHT_GREY)
    add_textbox(s, "Base Paper: Abdul Karim et al., IEEE Access, 2023  |  DOI: 10.1109/ACCESS.2023.3252366",
                Inches(0.6), Inches(5.75), Inches(12), Inches(0.4),
                font_size=Pt(11), italic=True, color=MID_GREY)

    slide_number(s, 1, TOTAL)
    add_notes(s, ("Title slide. Introduce the project, team, supervisor and institution. "
                  "Mention the base paper reference (IEEE Access 2023). "
                  "The system classifies URLs as PHISHING or LEGITIMATE using a hybrid ML model."))

    # ── Slide 2: Abstract ─────────────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Abstract")
    teal_accent_line(s)
    slide_number(s, 2, TOTAL)

    bullets = [
        "Phishing attacks are among the most prevalent and dangerous cyberthreats, targeting users through deceptive URLs.",
        "This project proposes a Hybrid Machine Learning System that classifies URLs as PHISHING or LEGITIMATE.",
        "Approach: Extract 15 lexical URL features → Train Random Forest + Logistic Regression → Combine via Voting Classifier.",
        "Dataset: 10,000 balanced URLs (5,000 phishing from PhishTank + 5,000 legitimate from Tranco/UNB).",
        "Hybrid model achieves 90.65% accuracy and 96.37% ROC-AUC on the held-out test set.",
        "Deployed as an interactive Streamlit web application for real-time URL inspection.",
    ]
    bullet_box(s, bullets, font_size=Pt(15))
    add_notes(s, ("Read the abstract aloud. Emphasise: no need for external APIs or WHOIS lookups — "
                  "all features are purely lexical (derived from the URL string itself). "
                  "Highlight the 90.65% accuracy figure."))

    # ── Slide 3: Introduction & Motivation ────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Introduction & Motivation", "Why is phishing detection critical?")
    teal_accent_line(s)
    slide_number(s, 3, TOTAL)

    bullets = [
        "Phishing is a social-engineering attack using fraudulent URLs to steal credentials and financial data.",
        "APWG reported >1.3 million unique phishing sites in Q3 2023 — a 17% year-on-year rise.",
        "Traditional defences (blacklists) fail against newly registered zero-day phishing domains.",
        "ML-based URL analysis offers fast, zero-day detection without browser plugins or DNS queries.",
        "Gap: Most single-classifier systems (RF or LR alone) trade accuracy vs. generalisation.",
        "Our solution: Hybrid Voting Classifier that combines strengths of both algorithms.",
    ]
    bullet_box(s, bullets)
    add_notes(s, ("Motivate the problem with recent statistics. Emphasise that blacklist-based tools "
                  "miss new phishing URLs until they are reported. ML-based lexical analysis works "
                  "on the URL alone — no internet connection required at inference time."))

    # ── Slide 4: Literature Survey ────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Literature Survey", "Review of existing phishing detection approaches")
    teal_accent_line(s)
    slide_number(s, 4, TOTAL)

    headers = ["Author / Year", "Method", "Accuracy", "Limitation"]
    rows = [
        ["Jain & Gupta, 2018",    "Rule-based + Heuristics",       "~89%",   "High false-positive rate"],
        ["Sahoo et al., 2019",    "LSTM on URL characters",         "~94%",   "Slow inference; large model"],
        ["Subasi et al., 2020",   "Random Forest (30 features)",    "~96%",   "Domain-specific features only"],
        ["Mohammad et al., 2021", "SVM + Phishtank",                "~93%",   "Requires external WHOIS calls"],
        ["Karim et al., 2023",    "Hybrid Voting (RF + LR + NB)",   "~97%",   "Complex feature engineering"],
        ["Our Work, 2025",        "Hybrid Voting (RF + LR)",        "90.65%", "Purely lexical; scalable"],
    ]
    add_table(s, headers, rows, t=Inches(1.45), h=Inches(5.7))
    add_notes(s, ("Walk through each paper briefly. Point out that Karim et al. (the base paper) "
                  "uses three classifiers including Naive Bayes; our adaptation uses two classifiers "
                  "for simplicity and achieves competitive accuracy with 15 features."))

    # ── Slide 5: Problem Statement ────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Problem Statement", "Input → Process → Output")
    teal_accent_line(s)
    slide_number(s, 5, TOTAL)

    # Three boxes
    box_w, box_h = Inches(3.8), Inches(4.5)
    gap = Inches(0.35)
    tops = Inches(1.6)
    for i, (label, items, fill) in enumerate([
        ("INPUT", [
            "A raw URL string",
            "e.g. http://login.verify-bank.com/update",
            "(No DNS / WHOIS queries needed)"
        ], DARK_BLUE),
        ("PROCESS", [
            "1. Extract 15 lexical features",
            "2. Apply StandardScaler (for LR)",
            "3. Random Forest prediction",
            "4. Logistic Regression prediction",
            "5. Soft Voting aggregation"
        ], RGBColor(0x0E, 0x6E, 0x8C)),
        ("OUTPUT", [
            "Label: PHISHING or LEGITIMATE",
            "Confidence score (%)",
            "Risk flags raised",
            "Actionable user warning"
        ], RGBColor(0x11, 0x72, 0x4F)),
    ]):
        left = gap + i * (box_w + gap)
        add_rect(s, left, tops, box_w, box_h, fill)
        add_textbox(s, label, left, tops + Inches(0.1), box_w, Inches(0.45),
                    font_size=Pt(18), bold=True, color=TEAL, align=PP_ALIGN.CENTER)
        body = "\n".join(f"• {x}" for x in items)
        add_textbox(s, body, left + Inches(0.1), tops + Inches(0.6),
                    box_w - Inches(0.2), box_h - Inches(0.7),
                    font_size=Pt(13), color=WHITE)
        # Arrow (except after last)
        if i < 2:
            arr_l = left + box_w + Inches(0.05)
            add_textbox(s, "→", arr_l, tops + Inches(1.8), gap + Inches(0.05), Inches(0.6),
                        font_size=Pt(28), bold=True, color=TEAL, align=PP_ALIGN.CENTER)

    add_notes(s, ("Explain the three-stage pipeline. Emphasise that the system is OFFLINE — "
                  "it only analyses the URL string. No network call is made during inference."))

    # ── Slide 6: Objectives ───────────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Objectives")
    teal_accent_line(s)
    slide_number(s, 6, TOTAL)

    bullets = [
        "O1 — Feature Engineering: Design and implement 15 lexical features directly from the URL string.",
        "O2 — Model Training: Train Random Forest and Logistic Regression classifiers independently.",
        "O3 — Hybrid Ensemble: Combine classifiers using a Soft Voting strategy to improve robustness.",
        "O4 — Rigorous Evaluation: Report accuracy, precision, recall, F1, ROC-AUC + 5-fold CV.",
        "O5 — Hyperparameter Tuning: Optimise model parameters via GridSearchCV to prevent overfitting.",
        "O6 — Deployment: Build an interactive Streamlit app for real-time URL classification.",
    ]
    bullet_box(s, bullets, font_size=Pt(15))
    add_notes(s, ("Six clear, measurable objectives. Each maps directly to a section of the implementation. "
                  "Mention that O4 and O5 address academic rigour — examiners look for these."))

    # ── Slide 7: Proposed Methodology ─────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Proposed Methodology", "System Architecture Overview")
    teal_accent_line(s)
    slide_number(s, 7, TOTAL)

    # Simple text-based architecture diagram
    stages = [
        ("Raw URL Input", DARK_BLUE),
        ("Feature Extraction (15 Lexical Features)", RGBColor(0x0E, 0x6E, 0x8C)),
        ("Train/Test Split  80% Train | 20% Test", RGBColor(0x11, 0x72, 0x4F)),
        ("Random Forest          Logistic Regression", DARK_BLUE),
        ("Soft Voting Classifier  (Hybrid Ensemble)", GOLD),
        ("PHISHING / LEGITIMATE + Confidence Score", RGBColor(0xC0, 0x39, 0x2B)),
    ]
    box_h_sm = Inches(0.62)
    box_w_sm = Inches(9)
    lft = Inches(2.15)
    for i, (label, fill) in enumerate(stages):
        top = Inches(1.45) + i * (box_h_sm + Inches(0.1))
        add_rect(s, lft, top, box_w_sm, box_h_sm, fill)
        add_textbox(s, label, lft, top + Inches(0.12), box_w_sm, box_h_sm - Inches(0.12),
                    font_size=Pt(15), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        if i < len(stages) - 1:
            add_textbox(s, "▼", lft + Inches(4.3), top + box_h_sm - Inches(0.05),
                        Inches(0.5), Inches(0.25),
                        font_size=Pt(12), color=TEAL, align=PP_ALIGN.CENTER)

    add_notes(s, ("Walk through each stage top-to-bottom. "
                  "The key innovation is the Soft Voting layer that averages predicted probabilities "
                  "from both classifiers, reducing variance compared to either alone."))

    # ── Slide 8: Implementation Plan ──────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Implementation Plan", "Step-by-step development roadmap")
    teal_accent_line(s)
    slide_number(s, 8, TOTAL)

    headers = ["Step", "Task", "Tools / Libraries", "Status"]
    rows = [
        ["1", "Dataset Collection & Cleaning",          "pandas, requests",          "DONE"],
        ["2", "Feature Extraction (15 features)",       "re, urllib, socket",        "DONE"],
        ["3", "Train/Test Split",                       "scikit-learn",              "DONE"],
        ["4", "Train RF & LR",                          "RandomForestClassifier, LR","DONE"],
        ["5", "Hyperparameter Tuning (GridSearchCV)",   "scikit-learn",              "DONE"],
        ["6", "Hybrid VotingClassifier",                "VotingClassifier",          "DONE"],
        ["7", "Evaluation (Metrics + Plots)",           "matplotlib, seaborn",       "DONE"],
        ["8", "Model Persistence",                      "joblib",                    "DONE"],
        ["9", "Streamlit Web App Deployment",           "streamlit",                 "DONE"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(5.65), font_size=Pt(11))
    add_notes(s, ("All 9 implementation steps are complete. The STATUS column shows DONE — "
                  "adjust to IN PROGRESS / PLANNED if presenting before full completion. "
                  "Examiners appreciate a clear traceability between plan and implementation."))

    # ── Slide 9: Hardware & Software Requirements ──────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Hardware & Software Requirements")
    teal_accent_line(s)
    slide_number(s, 9, TOTAL)

    # Two columns
    add_textbox(s, "Hardware", Inches(0.4), Inches(1.5), Inches(6), Inches(0.4),
                font_size=Pt(16), bold=True, color=DARK_BLUE)
    add_rect(s, Inches(0.4), Inches(1.9), Inches(6), Inches(4.5), DARK_BLUE)
    hw = [
        "Processor:  Intel Core i5 / AMD Ryzen 5 (or higher)",
        "RAM:  8 GB minimum (16 GB recommended)",
        "Storage:  SSD with 10 GB free space",
        "GPU:  Optional (CPU-only training supported)",
        "OS:  Windows 10/11 / Ubuntu 20.04+",
    ]
    add_textbox(s, "\n".join(f"• {x}" for x in hw),
                Inches(0.5), Inches(2.0), Inches(5.8), Inches(4.3),
                font_size=Pt(13), color=WHITE)

    add_textbox(s, "Software & Libraries", Inches(6.8), Inches(1.5), Inches(6), Inches(0.4),
                font_size=Pt(16), bold=True, color=DARK_BLUE)
    add_rect(s, Inches(6.8), Inches(1.9), Inches(6.1), Inches(4.5), RGBColor(0x0E, 0x6E, 0x8C))
    sw = [
        "Python 3.11",
        "pandas 2.x, numpy 1.x",
        "scikit-learn 1.x",
        "matplotlib, seaborn",
        "joblib  (model serialisation)",
        "streamlit  (web UI)",
        "python-pptx  (this presentation)",
        "Jupyter Notebook  (exploration)",
    ]
    add_textbox(s, "\n".join(f"• {x}" for x in sw),
                Inches(6.9), Inches(2.0), Inches(5.9), Inches(4.3),
                font_size=Pt(13), color=WHITE)
    slide_number(s, 9, TOTAL)
    add_notes(s, ("These are minimum requirements. The project was developed and tested on "
                  "Windows 11 with Python 3.11. All libraries are open-source and free."))

    # ── Slide 10: Novelty / Innovation ────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Novelty & Innovation", "What makes this project different?")
    teal_accent_line(s)
    slide_number(s, 10, TOTAL)

    bullets = [
        "Purely lexical features: No DNS, WHOIS, or external API calls — works offline.",
        "Hybrid Soft Voting: Averaged probability outputs reduce both bias (RF) and variance (LR).",
        "Token-based keyword matching: Avoids false positives on legitimate URLs (e.g., wikipedia/Phishing).",
        "Balanced 10,000-URL dataset: Equal phishing + legitimate samples for unbiased training.",
        "GridSearchCV tuning: Best hyperparameters found systematically, not by guesswork.",
        "End-to-end pipeline: From raw URL string → trained model → live Streamlit web app.",
    ]
    bullet_box(s, bullets, font_size=Pt(15))
    add_notes(s, ("This slide directly answers 'What is new in your project?' "
                  "The token-based keyword fix is a subtle but important improvement over naive "
                  "substring search. Emphasise the end-to-end nature — not just a notebook."))

    # ── Slide 11: Expected Outcome ────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Expected Outcome")
    teal_accent_line(s)
    slide_number(s, 11, TOTAL)

    headers = ["Metric", "Random Forest", "Logistic Regression", "Hybrid Voting (Ours)"]
    rows = [
        ["Accuracy",   "92.90%", "82.45%", "90.65%"],
        ["Precision",  "93.69%", "84.93%", "92.74%"],
        ["Recall",     "92.00%", "78.90%", "88.20%"],
        ["F1-Score",   "92.84%", "81.80%", "90.42%"],
        ["ROC-AUC",    "97.70%", "90.88%", "96.37%"],
        ["CV Accuracy","92.34%", "83.81%", "90.56%"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(4.8), font_size=Pt(12))
    add_textbox(s, "★ Hybrid model shows best generalisation (lowest CV variance ±0.0032)",
                Inches(0.4), Inches(6.45), Inches(12.5), Inches(0.4),
                font_size=Pt(13), bold=True, color=RGBColor(0xC0, 0x39, 0x2B))
    add_notes(s, ("These are the actual results from our trained model. "
                  "The Hybrid model has lower accuracy than RF alone but better generalisation "
                  "(lowest cross-validation standard deviation). Explain the bias-variance trade-off."))

    # ── Slide 12: Gantt Chart / Timeline ──────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Project Timeline", "Aug 2025 – Jan 2026")
    teal_accent_line(s)
    slide_number(s, 12, TOTAL)

    months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
    tasks = [
        ("Literature Survey & Problem Def.",  [1, 1, 0, 0, 0, 0]),
        ("Dataset Collection & Cleaning",     [0, 1, 1, 0, 0, 0]),
        ("Feature Engineering",               [0, 0, 1, 1, 0, 0]),
        ("Model Training & Tuning",           [0, 0, 0, 1, 1, 0]),
        ("Evaluation & Reporting",            [0, 0, 0, 0, 1, 1]),
        ("Web App Development",               [0, 0, 0, 0, 1, 1]),
        ("Documentation & Presentations",     [0, 0, 0, 0, 0, 1]),
    ]

    row_h = Inches(0.55)
    col_w = Inches(1.5)
    label_w = Inches(4.2)
    start_l = Inches(0.4)
    start_t = Inches(1.5)

    # Headers
    for mi, m in enumerate(months):
        add_textbox(s, m,
                    start_l + label_w + mi * col_w, start_t,
                    col_w, Inches(0.4),
                    font_size=Pt(12), bold=True, color=DARK_BLUE, align=PP_ALIGN.CENTER)

    for ti, (task_name, active) in enumerate(tasks):
        top = start_t + Inches(0.45) + ti * row_h
        add_textbox(s, task_name, start_l, top, label_w, row_h,
                    font_size=Pt(11), color=DARK_BLUE)
        for mi, on in enumerate(active):
            cell_l = start_l + label_w + mi * col_w + Inches(0.05)
            cell_t = top + Inches(0.05)
            fill = TEAL if on else LIGHT_GREY
            add_rect(s, cell_l, cell_t, col_w - Inches(0.1), row_h - Inches(0.1), fill)

    add_textbox(s, "■ = Active Month    (Teal = Planned/Completed)",
                start_l, Inches(6.9), Inches(6), Inches(0.4),
                font_size=Pt(10), color=MID_GREY)
    add_notes(s, ("Walk through the timeline month by month. By October the core model is complete. "
                  "November-December focus on evaluation and the web app. January is final documentation."))

    # ── Slide 13: Conclusion & References ─────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Conclusion & References")
    teal_accent_line(s)
    slide_number(s, 13, TOTAL)

    add_textbox(s, "Conclusion",
                Inches(0.4), Inches(1.45), Inches(12.5), Inches(0.4),
                font_size=Pt(16), bold=True, color=DARK_BLUE)
    conc_bullets = [
        "Designed a hybrid ML pipeline combining Random Forest and Logistic Regression for URL phishing detection.",
        "Achieved 90.65% test accuracy and 96.37% ROC-AUC with minimal cross-validation variance.",
        "The Streamlit web app provides real-time, offline URL inspection with confidence scores.",
        "Future Work: Browser extension, deep learning (BERT/LSTM), real-time threat-feed integration.",
    ]
    bullet_box(s, conc_bullets, t=Inches(1.9), h=Inches(2.2), font_size=Pt(14))

    add_textbox(s, "Key References",
                Inches(0.4), Inches(4.15), Inches(12.5), Inches(0.4),
                font_size=Pt(16), bold=True, color=DARK_BLUE)
    refs = [
        "[1] A. Karim et al., 'Phishing Detection System Through Hybrid ML Based on URL,' IEEE Access, 2023.",
        "[2] APWG Phishing Activity Trends Reports, 2023.",
        "[3] F. Pedregosa et al., 'Scikit-learn: ML in Python,' JMLR, 2011.",
        "[4] PhishTank — openphish.com / phishtank.org",
        "[5] Tranco List — tranco-list.eu",
    ]
    bullet_box(s, refs, t=Inches(4.6), h=Inches(2.6), font_size=Pt(12))
    add_notes(s, ("Wrap up by linking the project back to the objectives. "
                  "Mention future directions briefly — this shows forward thinking to examiners."))

    out = r"C:\Major_Project\Phishing_Abstract_Presentation.pptx"
    prs.save(out)
    print(f"[OK] Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# DECK 2 – EXECUTION PRESENTATION  (17 slides)
# ══════════════════════════════════════════════════════════════════════════════

def build_execution_deck():
    prs = new_prs()
    TOTAL = 17

    # ── Slide 1: Title ────────────────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, DARK_BLUE)
    add_rect(s, Inches(0), Inches(4.8), SLIDE_W, Inches(0.08), TEAL)
    add_rect(s, Inches(0), Inches(6.5), SLIDE_W, Inches(0.08), TEAL)

    add_textbox(s, "Phishing Detection System",
                Inches(0.5), Inches(0.9), Inches(12.3), Inches(0.9),
                font_size=Pt(34), bold=True, color=TEAL, align=PP_ALIGN.CENTER)
    add_textbox(s, "Through Hybrid Machine Learning Based on URL",
                Inches(0.5), Inches(1.7), Inches(12.3), Inches(0.7),
                font_size=Pt(24), color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, "Execution / Implementation Presentation",
                Inches(0.5), Inches(2.55), Inches(12.3), Inches(0.5),
                font_size=Pt(16), italic=True, color=LIGHT_GREY, align=PP_ALIGN.CENTER)
    add_rect(s, Inches(1.5), Inches(3.2), Inches(10.3), Pt(1.5), TEAL)

    add_textbox(s, "Team Members:",
                Inches(0.6), Inches(3.4), Inches(6), Inches(0.35),
                font_size=Pt(13), bold=True, color=TEAL)
    add_textbox(s,
                "Pasula Udaya  |  Sadiya Masarrath  |  Pulugu Kumar Reddy\n"
                "Sampangi Nithin  |  Penchala Hansika",
                Inches(0.6), Inches(3.75), Inches(12), Inches(0.7),
                font_size=Pt(13), color=WHITE)
    add_textbox(s, "Supervisor: S. Ravi  |  Coordinator: Dr. A. Godavari",
                Inches(0.6), Inches(4.55), Inches(12), Inches(0.4),
                font_size=Pt(12), color=LIGHT_GREY)
    add_textbox(s, "Dept. of CSE (Networks)  |  KITSW, Warangal  |  2025-2026",
                Inches(0.6), Inches(4.95), Inches(12), Inches(0.4),
                font_size=Pt(12), color=LIGHT_GREY)
    slide_number(s, 1, TOTAL)
    add_notes(s, ("Execution deck — this presentation focuses on WHAT WAS BUILT AND RESULTS. "
                  "About 30% background, 70% implementation and results."))

    # ── Slide 2: Problem & Objectives (Recap) ─────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Problem & Objectives — Recap")
    teal_accent_line(s)
    slide_number(s, 2, TOTAL)

    bullets = [
        "Problem: Attackers craft deceptive URLs to steal credentials — blacklists can't keep up.",
        "Goal: Classify any URL as PHISHING or LEGITIMATE in real time using ML.",
        "Input: Raw URL string only — no DNS / WHOIS lookups required.",
        "O1: Extract 15 lexical features from URL.    O2: Train RF and LR models.",
        "O3: Combine into Hybrid Soft Voting Classifier.",
        "O4: Evaluate rigorously (accuracy, F1, ROC-AUC, CV).    O5: Deploy via Streamlit.",
    ]
    bullet_box(s, bullets, font_size=Pt(15))
    add_notes(s, ("Quick recap — examiners may not remember the abstract presentation. "
                  "Keep this to 1-2 minutes."))

    # ── Slide 3: Literature Gap ────────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Literature Gap & Our Contribution")
    teal_accent_line(s)
    slide_number(s, 3, TOTAL)

    headers = ["Gap in Existing Work", "Our Solution"]
    rows = [
        ["External API dependency (WHOIS, DNS)", "100% lexical features — offline inference"],
        ["Single classifier — high variance",    "Hybrid Voting — lower variance, robust"],
        ["Substring keyword matching → FP",      "Token intersection — no false positives"],
        ["Imbalanced / small datasets",          "10,000 balanced URLs (50/50 split)"],
        ["No real-time deployment",              "Streamlit app with confidence scores"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(5.6), font_size=Pt(13))
    add_notes(s, ("Each row maps one identified gap to our concrete solution. "
                  "This demonstrates awareness of the state of the art."))

    # ── Slide 4: System Architecture ──────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Proposed System Architecture")
    teal_accent_line(s)
    slide_number(s, 4, TOTAL)

    stages = [
        ("URL Input",                           DARK_BLUE),
        ("Feature Extractor (features.py)",     RGBColor(0x0E, 0x6E, 0x8C)),
        ("StandardScaler  (for LR pipeline)",   RGBColor(0x11, 0x72, 0x4F)),
        ("Random Forest (n=150)       Logistic Regression (C=0.1)", DARK_BLUE),
        ("Soft Voting Classifier  — averaged P(phishing)",           GOLD),
        ("Prediction: PHISHING / LEGITIMATE  +  Confidence %",      RGBColor(0xC0, 0x39, 0x2B)),
    ]
    box_h_sm = Inches(0.65)
    box_w_sm = Inches(9.5)
    lft = Inches(1.9)
    for i, (label, fill) in enumerate(stages):
        top = Inches(1.45) + i * (box_h_sm + Inches(0.08))
        add_rect(s, lft, top, box_w_sm, box_h_sm, fill)
        add_textbox(s, label, lft, top + Inches(0.1), box_w_sm, box_h_sm - Inches(0.1),
                    font_size=Pt(14), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        if i < len(stages) - 1:
            add_textbox(s, "▼", lft + Inches(4.5), top + box_h_sm,
                        Inches(0.5), Inches(0.18),
                        font_size=Pt(10), color=TEAL, align=PP_ALIGN.CENTER)
    add_notes(s, ("The StandardScaler is applied INSIDE the LR pipeline — no data leakage. "
                  "RF does not need scaling. Both feed into the VotingClassifier."))

    # ── Slide 5: Dataset Details ───────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Dataset Details", "Source, size, and class distribution")
    teal_accent_line(s)
    slide_number(s, 5, TOTAL)

    headers = ["Property", "Value"]
    rows = [
        ["Total URLs",           "10,000"],
        ["Phishing (label = 1)", "5,000  (50%)  — Source: PhishTank verified feed"],
        ["Legitimate (label = 0)","5,000  (50%)  — Source: Tranco Top-1M + UNB Benign List"],
        ["Train set (80%)",      "8,000 URLs"],
        ["Test set (20%)",       "2,000 URLs"],
        ["Duplicate removal",    "Applied — URL-level deduplication"],
        ["Null handling",        "Applied — rows with empty URL dropped"],
        ["Class balance",        "Perfectly balanced (stratified split used)"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(5.2), font_size=Pt(12))
    add_textbox(s, "[INSERT: Bar chart of class distribution — 5000 Phishing vs 5000 Legitimate]",
                Inches(0.4), Inches(6.55), Inches(12.5), Inches(0.7),
                font_size=Pt(11), italic=True, color=GOLD)
    add_notes(s, ("Replace the placeholder with an actual bar chart from your Jupyter notebook. "
                  "Mention that PhishTank URLs are verified by community voting — high quality labels."))

    # ── Slide 6: Data Cleaning & Preprocessing ────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Data Cleaning & Preprocessing")
    teal_accent_line(s)
    slide_number(s, 6, TOTAL)

    bullets = [
        "Step 1 — Load raw PhishTank CSV and Tranco/UNB legitimate URL list into pandas DataFrame.",
        "Step 2 — Remove duplicate URLs (df.drop_duplicates('url')).",
        "Step 3 — Drop rows with null or empty URL values (df.dropna(subset=['url'])).",
        "Step 4 — Balance classes: sample 5,000 from each label using stratified selection.",
        "Step 5 — Apply extract_features() to each URL → build 15-column feature matrix.",
        "Step 6 — Train/test split with stratify=y to maintain 50/50 ratio in both sets.",
    ]
    bullet_box(s, bullets, h=Inches(4.0), font_size=Pt(14))
    add_textbox(s, "[INSERT SCREENSHOT: Jupyter notebook cell showing df.head() and df.info() output]",
                Inches(0.4), Inches(5.65), Inches(12.5), Inches(0.6),
                font_size=Pt(12), italic=True, color=GOLD)
    add_notes(s, ("Emphasise stratified split — prevents class imbalance in test set. "
                  "Replace placeholder with a real screenshot from your notebook."))

    # ── Slide 7: Feature Extraction — Table ───────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Feature Extraction", "15 Lexical URL Features")
    teal_accent_line(s)
    slide_number(s, 7, TOTAL)

    headers = ["#", "Feature Name", "Description", "Example Value"]
    rows = [
        ["1",  "url_length",          "Total character count of URL",          "54"],
        ["2",  "hostname_length",      "Length of hostname segment",            "22"],
        ["3",  "num_dots",            "Count of '.' in URL",                   "3"],
        ["4",  "num_hyphens",         "Count of '-' in URL",                   "2"],
        ["5",  "num_at",              "Count of '@' symbols",                  "0"],
        ["6",  "num_digits",          "Count of digit characters",             "4"],
        ["7",  "num_special_chars",   "Count of special chars (!$%^&*)",        "1"],
        ["8",  "has_ip",              "1 if hostname is an IP address",         "0"],
        ["9",  "has_https",           "1 if scheme is HTTPS",                  "0"],
        ["10", "num_subdomains",      "Number of subdomain levels",            "2"],
        ["11", "num_path_levels",     "Depth of URL path",                     "3"],
        ["12", "has_suspicious_kw",   "1 if URL has login/verify/bank etc.",    "1"],
        ["13", "is_shortened",        "1 if domain is a URL shortener",        "0"],
        ["14", "has_double_slash",    "1 if '//' appears in path",             "1"],
        ["15", "has_port",            "1 if explicit port in URL",             "0"],
    ]
    add_table(s, headers, rows, t=Inches(1.45), h=Inches(5.75), font_size=Pt(10))
    add_notes(s, ("Walk through 2-3 features in detail. Highlight has_ip and has_suspicious_kw "
                  "as the most intuitive indicators. Mention that url_length and has_https "
                  "are the top two by feature importance."))

    # ── Slide 8: Feature Extraction Code & Sample ─────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Feature Extraction — Code & Sample Output")
    teal_accent_line(s)
    slide_number(s, 8, TOTAL)

    code = (
        "from src.features import extract_features\n\n"
        "url = 'http://login.verify-bank.com/update/account?id=123'\n"
        "features = extract_features(url, as_dict=True)\n\n"
        "# Sample output:\n"
        "# url_length        : 53\n"
        "# hostname_length   : 22\n"
        "# num_dots          : 3\n"
        "# has_https         : 0     ← HTTP only!\n"
        "# has_suspicious_kw : 1     ← 'login', 'verify', 'bank', 'update'\n"
        "# num_subdomains    : 1\n"
        "# has_ip            : 0\n"
        "# ... (all 15 features)"
    )
    add_rect(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(4.0), RGBColor(0x1E, 0x1E, 0x1E))
    add_textbox(s, code,
                Inches(0.5), Inches(1.55), Inches(12.3), Inches(3.9),
                font_size=Pt(12), color=RGBColor(0xCE, 0xF5, 0x9D),
                font_name="Courier New")

    add_textbox(s, "[INSERT SCREENSHOT: Terminal/Notebook showing actual extract_features() output]",
                Inches(0.4), Inches(5.65), Inches(12.5), Inches(0.6),
                font_size=Pt(12), italic=True, color=GOLD)
    add_notes(s, ("Show the code snippet live if possible. Replace the placeholder with "
                  "a real terminal screenshot. Point out the suspicious keyword detection "
                  "using token intersection — not substring match."))

    # ── Slide 9: Train/Test Split & Model Training ────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Model Training", "Random Forest & Logistic Regression")
    teal_accent_line(s)
    slide_number(s, 9, TOTAL)

    headers = ["Parameter", "Random Forest", "Logistic Regression"]
    rows = [
        ["Algorithm",          "Ensemble of Decision Trees",     "Linear Discriminant Boundary"],
        ["Best n_estimators",  "150",                            "N/A"],
        ["Best max_depth",     "25",                             "N/A"],
        ["Best min_samples_split", "5",                          "N/A"],
        ["Best C (regularisation)", "N/A",                       "0.1  (L2 penalty)"],
        ["Best solver",        "N/A",                            "lbfgs"],
        ["Feature scaling",    "Not required",                   "StandardScaler applied"],
        ["Search method",      "GridSearchCV (5-fold)",          "GridSearchCV (5-fold)"],
        ["Training samples",   "8,000",                          "8,000"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(5.65), font_size=Pt(11))
    add_notes(s, ("Explain why LR needs scaling (gradient-based optimisation is sensitive to feature scale) "
                  "but RF does not (tree splits are scale-invariant). "
                  "GridSearchCV runs each combination on 5 folds — avoids overfitting the val set."))

    # ── Slide 10: Hybrid Voting Classifier ────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Hybrid Voting Classifier", "Soft vs Hard Voting")
    teal_accent_line(s)
    slide_number(s, 10, TOTAL)

    bullets = [
        "Hard Voting: Each classifier predicts a label; majority vote wins. Fast but ignores confidence.",
        "Soft Voting: Average the predicted probabilities; pick label with higher mean probability.",
        "Why Soft? — Preserves uncertainty information. Better when classifiers are well-calibrated.",
        "Our hybrid: VotingClassifier([('rf', rf), ('lr', lr_pipeline)], voting='soft', weights=[1,1])",
        "Equal weights chosen after comparing [2,1] and [1,1] on validation set (soft [1,1] wins).",
    ]
    bullet_box(s, bullets, h=Inches(3.5), font_size=Pt(14))

    code2 = (
        "from sklearn.ensemble import VotingClassifier\n"
        "hybrid = VotingClassifier(\n"
        "    estimators=[('rf', best_rf), ('lr', lr_pipeline)],\n"
        "    voting='soft',\n"
        "    weights=[1, 1]\n"
        ")\n"
        "hybrid.fit(X_train, y_train)"
    )
    add_rect(s, Inches(0.4), Inches(5.1), Inches(12.5), Inches(1.9), RGBColor(0x1E, 0x1E, 0x1E))
    add_textbox(s, code2,
                Inches(0.5), Inches(5.15), Inches(12.3), Inches(1.8),
                font_size=Pt(12), color=RGBColor(0xCE, 0xF5, 0x9D),
                font_name="Courier New")
    add_notes(s, ("The LR is wrapped in a Pipeline to include the StandardScaler inside the estimator. "
                  "This is crucial — otherwise the scaler would need to be applied before the "
                  "VotingClassifier, which complicates inference."))

    # ── Slide 11: Evaluation Metrics Table ────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Evaluation Results", "Model Comparison on Test Set (2,000 URLs)")
    teal_accent_line(s)
    slide_number(s, 11, TOTAL)

    headers = ["Metric", "Logistic Regression", "Random Forest", "Hybrid Voting (Ours)"]
    rows = [
        ["Accuracy",    "82.45%", "92.90%", "90.65%"],
        ["Precision",   "84.93%", "93.69%", "92.74%"],
        ["Recall",      "78.90%", "92.00%", "88.20%"],
        ["Specificity", "86.00%", "93.80%", "93.10%"],
        ["F1-Score",    "81.80%", "92.84%", "90.42%"],
        ["ROC-AUC",     "90.88%", "97.70%", "96.37%"],
        ["CV Accuracy", "83.81% ±1.21%", "92.34% ±0.51%", "90.56% ±0.32%"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(5.2), font_size=Pt(12))
    add_textbox(s, "★ Hybrid achieves best CV stability (lowest variance ±0.32%)  |  [Values are ACTUAL results — do NOT replace]",
                Inches(0.4), Inches(6.75), Inches(12.5), Inches(0.5),
                font_size=Pt(11), bold=True, color=RGBColor(0xC0, 0x39, 0x2B))
    add_notes(s, ("Emphasise that these are real results from the trained model. "
                  "The Hybrid has lower raw accuracy than RF but better generalisation "
                  "(lower CV standard deviation). This is the key academic contribution."))

    # ── Slide 12: Confusion Matrix & ROC Curve ────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Confusion Matrix & ROC Curve")
    teal_accent_line(s)
    slide_number(s, 12, TOTAL)

    cm_path  = r"C:\Major_Project\reports\confusion_matrices.png"
    roc_path = r"C:\Major_Project\reports\roc_curves.png"

    if os.path.exists(cm_path):
        s.shapes.add_picture(cm_path,  Inches(0.2),  Inches(1.4), Inches(6.4), Inches(5.7))
    else:
        add_textbox(s, "[INSERT: confusion_matrices.png]",
                    Inches(0.2), Inches(1.4), Inches(6.4), Inches(5.7),
                    font_size=Pt(14), italic=True, color=GOLD)

    if os.path.exists(roc_path):
        s.shapes.add_picture(roc_path, Inches(6.7), Inches(1.4), Inches(6.4), Inches(5.7))
    else:
        add_textbox(s, "[INSERT: roc_curves.png]",
                    Inches(6.7), Inches(1.4), Inches(6.4), Inches(5.7),
                    font_size=Pt(14), italic=True, color=GOLD)

    add_notes(s, ("Left: Confusion matrices for all three models — point out True Positive (TP) "
                  "and False Negative (FN) counts. A FN here means a phishing URL is missed. "
                  "Right: ROC curves — RF achieves AUC 0.977, Hybrid 0.964. "
                  "Higher AUC = better discrimination ability."))

    # ── Slide 13: Feature Importance ─────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Random Forest Feature Importance")
    teal_accent_line(s)
    slide_number(s, 13, TOTAL)

    fi_path = r"C:\Major_Project\reports\feature_importance.png"
    if os.path.exists(fi_path):
        s.shapes.add_picture(fi_path, Inches(0.3), Inches(1.4), Inches(8.0), Inches(5.7))
    else:
        add_textbox(s, "[INSERT: feature_importance.png]",
                    Inches(0.3), Inches(1.4), Inches(8.0), Inches(5.7),
                    font_size=Pt(14), italic=True, color=GOLD)

    headers2 = ["Rank", "Feature", "Importance"]
    rows2 = [
        ["1", "url_length",        "23.74%"],
        ["2", "has_https",         "16.96%"],
        ["3", "hostname_length",   "14.41%"],
        ["4", "num_path_levels",   "12.52%"],
        ["5", "num_digits",        "12.21%"],
    ]
    add_table(s, headers2, rows2, l=Inches(8.5), t=Inches(1.5),
              w=Inches(4.6), h=Inches(3.5), font_size=Pt(11))
    add_textbox(s, "Top 5 features drive >79% of classification decisions",
                Inches(8.5), Inches(5.1), Inches(4.6), Inches(0.5),
                font_size=Pt(12), bold=True, color=DARK_BLUE)
    add_notes(s, ("URL length is the single most discriminative feature — phishing URLs tend "
                  "to be longer. HTTPS presence is second — many phishing sites now use HTTPS "
                  "so its absence is a strong indicator. Number of digits often indicates "
                  "randomly generated hostnames."))

    # ── Slide 14: Cross-Validation & Hyperparameter Tuning ───────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Cross-Validation & Hyperparameter Tuning")
    teal_accent_line(s)
    slide_number(s, 14, TOTAL)

    add_textbox(s, "5-Fold Cross-Validation Results",
                Inches(0.4), Inches(1.45), Inches(12), Inches(0.4),
                font_size=Pt(16), bold=True, color=DARK_BLUE)
    cv_headers = ["Model", "Mean CV Accuracy", "Std Dev", "Interpretation"]
    cv_rows = [
        ["Random Forest",         "92.34%", "±0.51%", "High accuracy, stable"],
        ["Logistic Regression",   "83.81%", "±1.21%", "Lower accuracy, more variance"],
        ["Hybrid Voting (Soft)",  "90.56%", "±0.32%", "Best stability — least overfitting"],
    ]
    add_table(s, cv_headers, cv_rows, t=Inches(1.9), h=Inches(1.8), font_size=Pt(12))

    add_textbox(s, "GridSearchCV Parameter Search Space",
                Inches(0.4), Inches(3.8), Inches(12), Inches(0.4),
                font_size=Pt(16), bold=True, color=DARK_BLUE)
    gs_headers = ["Model", "Parameters Searched", "Best Values Found"]
    gs_rows = [
        ["Random Forest", "n_estimators: [50,100,150] | max_depth: [10,20,25] | min_samples_split: [2,5,10]",
         "n=150, depth=25, split=5"],
        ["Logistic Reg.", "C: [0.01,0.1,1,10] | solver: [lbfgs,liblinear]",
         "C=0.1, solver=lbfgs"],
    ]
    add_table(s, gs_headers, gs_rows, t=Inches(4.25), h=Inches(2.2), font_size=Pt(11))
    add_notes(s, ("Cross-validation uses only the TRAINING set — the 20% test set is never seen "
                  "during tuning. This is essential for unbiased evaluation. "
                  "The hybrid's low std dev (0.32%) shows it generalises consistently."))

    # ── Slide 15: Working Demo ────────────────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Working Demo — Streamlit Web App")
    teal_accent_line(s)
    slide_number(s, 15, TOTAL)

    # Four placeholder boxes for screenshots
    demo_examples = [
        ("PHISHING  — Confidence: ~92%",
         "http://login.verify-bank.com/update/account",
         RGBColor(0xC0, 0x39, 0x2B)),
        ("PHISHING  — Confidence: ~88%",
         "http://192.168.1.1/paypal/login.php",
         RGBColor(0xC0, 0x39, 0x2B)),
        ("LEGITIMATE — Confidence: ~96%",
         "https://www.google.com/search?q=python",
         RGBColor(0x11, 0x72, 0x4F)),
        ("LEGITIMATE — Confidence: ~91%",
         "https://github.com/scikit-learn/scikit-learn",
         RGBColor(0x11, 0x72, 0x4F)),
    ]
    bw = Inches(6.0)
    bh = Inches(2.55)
    for i, (verdict, url, fill) in enumerate(demo_examples):
        col = i % 2
        row = i // 2
        left = Inches(0.3) + col * (bw + Inches(0.7))
        top = Inches(1.45) + row * (bh + Inches(0.15))
        add_rect(s, left, top, bw, bh, fill)
        add_textbox(s, verdict,
                    left + Inches(0.1), top + Inches(0.08), bw - Inches(0.2), Inches(0.45),
                    font_size=Pt(14), bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_textbox(s, url,
                    left + Inches(0.1), top + Inches(0.55), bw - Inches(0.2), Inches(0.4),
                    font_size=Pt(11), color=LIGHT_GREY, align=PP_ALIGN.CENTER)
        add_textbox(s, "[INSERT SCREENSHOT of app result for this URL]",
                    left + Inches(0.1), top + Inches(1.0), bw - Inches(0.2), Inches(1.4),
                    font_size=Pt(11), italic=True, color=GOLD, align=PP_ALIGN.CENTER)

    add_notes(s, ("Run the Streamlit app: 'streamlit run app.py' or visit http://localhost:8501. "
                  "Take screenshots for each of the 4 example URLs shown here. "
                  "Replace each [INSERT SCREENSHOT] placeholder with the actual app screenshot."))

    # ── Slide 16: Challenges & Solutions ─────────────────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Challenges Faced & Solutions")
    teal_accent_line(s)
    slide_number(s, 16, TOTAL)

    headers = ["#", "Challenge", "Solution Adopted"]
    rows = [
        ["1", "Old dataset had pre-extracted features — bypassed our feature extractor",
              "Switched to raw PhishTank feed + UNB URLs; built feature matrix from scratch"],
        ["2", "Legitimate URLs classified as phishing (wikipedia, stackoverflow)",
              "Added UNB benign URLs + expanded path templates in training data"],
        ["3", "Substring keyword match: 'Phishing' in wikipedia URL → false positive",
              "Replaced with token intersection: split URL on non-alphanumeric chars first"],
        ["4", "LR inside VotingClassifier needs its own scaler (no data leakage)",
              "Wrapped LR in sklearn Pipeline([scaler, clf]) so scaling is internal"],
        ["5", "Unicode print character caused Windows cp1252 encoding error",
              "Replaced '✓' with '[OK]' in print statements"],
    ]
    add_table(s, headers, rows, t=Inches(1.5), h=Inches(5.65), font_size=Pt(11))
    add_notes(s, ("This slide shows you solved real engineering problems — not just ran a notebook. "
                  "Challenge 3 (keyword matching) and Challenge 4 (pipeline design) show "
                  "deeper ML understanding. Examiners value this."))

    # ── Slide 17: Conclusion, Future Work & References ────────────────────────
    s = blank_slide(prs)
    fill_bg(s, LIGHT_GREY)
    header_bar(s, "Conclusion, Future Work & References")
    teal_accent_line(s)
    slide_number(s, 17, TOTAL)

    add_textbox(s, "Conclusion",
                Inches(0.4), Inches(1.45), Inches(12.5), Inches(0.4),
                font_size=Pt(15), bold=True, color=DARK_BLUE)
    conc = [
        "Successfully built an end-to-end phishing URL detection system using 15 lexical features.",
        "Hybrid Soft Voting (RF + LR) achieves 90.65% accuracy and best CV stability (±0.32%).",
        "Deployed as a live Streamlit web app — no internet connection required at inference time.",
        "100% pass rate on 10-URL manual test suite (5 phishing + 5 legitimate).",
    ]
    bullet_box(s, conc, t=Inches(1.9), h=Inches(1.7), font_size=Pt(13))

    add_textbox(s, "Future Work",
                Inches(0.4), Inches(3.7), Inches(12.5), Inches(0.4),
                font_size=Pt(15), bold=True, color=DARK_BLUE)
    fut = [
        "Browser Extension: Real-time URL inspection integrated into Chrome/Firefox.",
        "Deep Learning: LSTM / BERT on character-level URL sequences for higher accuracy.",
        "Real-time Threat Feed: Integrate PhishTank API for live phishing URL database.",
        "Extended Features: WHOIS age, SSL certificate validity, page content analysis.",
    ]
    bullet_box(s, fut, t=Inches(4.15), h=Inches(1.7), font_size=Pt(13))

    add_textbox(s, "References",
                Inches(0.4), Inches(5.95), Inches(12.5), Inches(0.35),
                font_size=Pt(13), bold=True, color=DARK_BLUE)
    refs_small = [
        "[1] A. Karim et al., IEEE Access 2023 | DOI:10.1109/ACCESS.2023.3252366",
        "[2] scikit-learn: ML in Python — Pedregosa et al., JMLR 2011",
        "[3] PhishTank — phishtank.org | Tranco — tranco-list.eu | UNB Benign List",
    ]
    bullet_box(s, refs_small, t=Inches(6.3), h=Inches(1.1), font_size=Pt(11))
    add_notes(s, ("End with a strong summary. Remind the panel of the key number: 90.65% accuracy. "
                  "The browser extension future work shows real-world applicability."))

    out = r"C:\Major_Project\Phishing_Execution_Presentation.pptx"
    prs.save(out)
    print(f"[OK] Saved: {out}")
    return out


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating presentations...")
    p1 = build_abstract_deck()
    p2 = build_execution_deck()
    print("\nDone!")
    print(f"  Abstract  -> {p1}")
    print(f"  Execution -> {p2}")
