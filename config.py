"""
config.py — Single-source formatting configuration for GSA Symposium submissions.

Change values here to update ALL generated reports without touching other files.
"""

from docx.shared import Inches, Pt

# ─── Font & Text ────────────────────────────────────────────────────────────
FONT_NAME = "Arial"
FONT_SIZE_BODY = Pt(12)          # Body / abstract text
FONT_SIZE_HEADING = Pt(14)       # Section headings (e.g. "Abstract")
FONT_SIZE_NAME = Pt(14)          # Student name in the header
FONT_SIZE_CAPTION = Pt(12)       # Figure captions
FONT_COLOR_HEX = "000000"        # Black

# ─── Spacing & Indentation ──────────────────────────────────────────────────
SPACING_AFTER = Pt(6)            # 6 pt after each paragraph
SPACING_BEFORE_SECTION = Pt(30)  # Space before Abstract / Figures sections
LINE_SPACING = 1.0               # Single spacing

# ─── Page Layout ─────────────────────────────────────────────────────────────
PAGE_MARGIN = Inches(1.0)        # All four margins

# ─── Headshot ────────────────────────────────────────────────────────────────
HEADSHOT_WIDTH = Inches(2.0)
HEADSHOT_HEIGHT = Inches(2.0)
HEADER_GUTTER = Inches(0.2)      # Space between headshot and info block

# ─── Figures ─────────────────────────────────────────────────────────────────
FIGURE_MAX_WIDTH = Inches(3.0)   # Per figure (side-by-side ≈ 48% of 6.5")
FIGURE_MAX_HEIGHT = Inches(2.5)

# ─── Validation ──────────────────────────────────────────────────────────────
ABSTRACT_MAX_WORDS_TOTAL = 300
ABSTRACT_MAX_WORDS_P1 = 200
RESEARCH_TOPIC_MAX_WORDS = 50
CAPTION_MAX_WORDS = 50
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png"]

# ─── Email ───────────────────────────────────────────────────────────────────
ADMIN_EMAIL = "skatuwal@unr.edu"
