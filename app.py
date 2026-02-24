"""
app.py  GSA Graduate Student Symposium Submission.
Run:  streamlit run app.py
"""

import streamlit as st
from docx_generator import generate_docx
import config as C

# ── Page config  (wide so we have room for a preview pane) ───────────────────
st.set_page_config(
    page_title="GSA Symposium Submission",
    page_icon="🎓",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', Arial, sans-serif; }

.main-header {
    background: linear-gradient(135deg,#003366 0%,#00508a 60%,#0073bf 100%);
    color:white; padding:1.4rem 2rem; border-radius:10px;
    margin-bottom:1.2rem; text-align:center;
}
.main-header h1 { margin:0 0 .2rem 0; font-size:1.5rem; font-weight:700; }
.main-header p  { margin:0; font-size:.88rem; opacity:.9; }

.section-divider {
    border:none; height:2px;
    background:linear-gradient(90deg,transparent,#0073bf,transparent);
    margin:1.1rem 0;
}
.info-box {
    background:#f0f6ff; border-left:4px solid #0073bf;
    padding:.65rem 1rem; border-radius:6px; font-size:.85rem;
    margin-bottom:.8rem; color:#1a1a1a;
}
.wc-ok  { font-size:.78rem; color:#555;   text-align:right; margin:-4px 0 6px 0; }
.wc-red { font-size:.78rem; color:#d32f2f; font-weight:600; text-align:right; margin:-4px 0 6px 0; }

/* ── Preview pane ── */
.preview-wrap {
    position:sticky; top:1rem;
    background:#fff; border:1.5px solid #c9d8ea;
    border-radius:10px; padding:0; overflow:hidden;
    box-shadow:0 2px 12px rgba(0,0,0,.08);
}
.preview-header {
    background:#003366; color:#fff;
    padding:.55rem 1rem; font-size:.85rem; font-weight:600;
}
.preview-body { padding:.9rem 1.1rem; }

/* Simulated document page */
.doc-page {
    background:#fff; border:1px solid #d0d0d0;
    padding:28px 30px; font-family:Arial,Helvetica,sans-serif;
    font-size:11.5px; color:#111; line-height:1.45;
    min-height:400px; border-radius:4px;
    box-shadow:0 1px 6px rgba(0,0,0,.1);
}
.doc-page .doc-name  { font-size:14px; font-weight:bold; margin-bottom:4px; }
.doc-page .doc-label { font-weight:bold; }
.doc-page .doc-heading{ font-size:13px; font-weight:bold; margin:10px 0 4px 0; }
.doc-page .doc-para   { margin-bottom:6px; text-align:justify; }
.doc-page .fig-row    { display:flex; gap:10px; margin-top:10px; }
.doc-page .fig-col    { flex:1; text-align:center; }
.doc-page .fig-cap    { font-size:10px; font-style:italic; text-align:left; margin-top:3px; }
.doc-page .doc-info   { margin-left:8px; }
.doc-page .header-row { display:flex; gap:12px; margin-bottom:8px; }
.doc-page .headshot-box{
    width:80px; height:80px; background:#e8ecf0;
    border:1px solid #bbb; border-radius:3px;
    display:flex; align-items:center; justify-content:center;
    font-size:9px; color:#888; flex-shrink:0;
}
.wc-badge-ok  { background:#e8f5e9; color:#2e7d32; padding:1px 7px;
                border-radius:10px; font-size:.75rem; font-weight:600; }
.wc-badge-red { background:#ffebee; color:#c62828; padding:1px 7px;
                border-radius:10px; font-size:.75rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _wc(text):
    return len(text.split()) if text and text.strip() else 0

def _badge(count, limit):
    cls = "wc-badge-red" if count > limit else "wc-badge-ok"
    return f'<span class="{cls}">{count}/{limit} words</span>'

def _wc_line(count, limit):
    cls = "wc-red" if count > limit else "wc-ok"
    return f'<div class="{cls}">{count} / {limit} words</div>'

def _validate_email(email):
    return "@" in email and "." in email.split("@")[-1]

def _file_too_large(f):
    return f is not None and len(f.getvalue()) > C.MAX_IMAGE_SIZE_MB * 1024 * 1024

def _esc(text):
    return (text or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ── Layout constants ──────────────────────────────────────────────────────────
LAYOUT_TEXT_ONLY = f"Text only — single paragraph (max {C.ABSTRACT_MAX_WORDS_TOTAL} words)"
LAYOUT_TWO_PARA  = f"Two paragraphs (max {C.ABSTRACT_MAX_WORDS_TOTAL} words total)"
LAYOUT_PARA_FIGS = "One paragraph + figure(s) (max 200 words)"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>Graduate student symposium <br> <span style="font-size: 0.85em; opacity: 0.9;">(Department of Civil and Environmental Engineering)</span></h1>
  <p>Fill in the form on the left; the right panel previews your formatted page in real time.</p>
</div>""", unsafe_allow_html=True)

# ── Two-column split ──────────────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

# ════════════════════════════════════════════════════════════════════════════
#  LEFT COLUMN — all inputs (no st.form so every widget triggers a rerender)
# ════════════════════════════════════════════════════════════════════════════
with left:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("👤 Student Information")

    c1, c2 = st.columns(2)
    with c1:
        student_name     = st.text_input("Full Name *",         placeholder="e.g., Jane Doe")
        graduate_program = st.text_input("Graduate Program *",  placeholder="e.g., Civil Eng.")
        degree           = st.selectbox("Degree *",             ["MS", "PhD"])
        year             = st.text_input("Graduation Year *",   placeholder="2026")
    with c2:
        contact_email = st.text_input("Contact Email *",    placeholder="email@unr.edu")
        advisor       = st.text_input("Advisor *",          placeholder="Dr. Smith")
        sponsor       = st.text_input("Sponsor (Optional)", placeholder="NSF, DOT…")
        career_goal   = st.selectbox("Career Goal *",       ["Academic","Industry","Public sector"])

    research_topic = st.text_area(f"Research Topic * (max {C.RESEARCH_TOPIC_MAX_WORDS} words)", placeholder="Title of your research", height=68)
    topic_w = _wc(research_topic)
    st.markdown(_wc_line(topic_w, C.RESEARCH_TOPIC_MAX_WORDS), unsafe_allow_html=True)

    headshot = st.file_uploader(f"Headshot * (JPG/PNG, max {C.MAX_IMAGE_SIZE_MB} MB)",
                                 type=C.ALLOWED_IMAGE_TYPES)

    # ── Layout picker (outside form → triggers rerender immediately) ──────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.subheader("📝 Submission Layout")
    st.markdown('<div class="info-box">Choose a layout. '
                '<strong>Everything must fit on 1 page.</strong></div>',
                unsafe_allow_html=True)

    layout_choice = st.radio("Layout *",
                             [LAYOUT_TEXT_ONLY, LAYOUT_TWO_PARA, LAYOUT_PARA_FIGS],
                             label_visibility="collapsed")

    is_text_only      = layout_choice == LAYOUT_TEXT_ONLY
    is_two_paragraphs = layout_choice == LAYOUT_TWO_PARA
    is_figures        = layout_choice == LAYOUT_PARA_FIGS

    # ── Abstract inputs ───────────────────────────────────────────────────
    if is_text_only:
        abstract_p1 = st.text_area(f"Abstract *", height=200,
                                    placeholder="Enter your abstract…", key="p1a")
        abstract_p2 = ""
        p1w = _wc(abstract_p1)
        st.markdown(_wc_line(p1w, C.ABSTRACT_MAX_WORDS_TOTAL), unsafe_allow_html=True)

    elif is_two_paragraphs:
        abstract_p1 = st.text_area(f"Paragraph 1 *  (max {C.ABSTRACT_MAX_WORDS_P1} words)",
                                    height=150, placeholder="First paragraph…", key="p1b")
        p1w = _wc(abstract_p1)
        st.markdown(_wc_line(p1w, C.ABSTRACT_MAX_WORDS_P1), unsafe_allow_html=True)

        remaining = max(0, C.ABSTRACT_MAX_WORDS_TOTAL - p1w)
        abstract_p2 = st.text_area(
            f"Paragraph 2 *  (max {remaining} words remaining)",
            height=150, placeholder="Second paragraph…", key="p2b")
        p2w = _wc(abstract_p2)
        st.markdown(_wc_line(p1w + p2w, C.ABSTRACT_MAX_WORDS_TOTAL), unsafe_allow_html=True)

    else:  # figures
        abstract_p1 = st.text_area("Abstract *  (max 200 words)",
                                    height=170, placeholder="Enter your abstract…", key="p1c")
        abstract_p2 = ""
        p1w = _wc(abstract_p1)
        st.markdown(_wc_line(p1w, 200), unsafe_allow_html=True)

    # ── Figures (Option 3 only) ───────────────────────────────────────────
    figure_1 = caption_1 = figure_2 = caption_2 = None
    if is_figures:
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.subheader("📊 Figures")
        st.markdown('<div class="info-box">'
                    'Max <strong>10 MB</strong> each. '
                    'One figure → centered. Two → side-by-side, left-aligned captions.'
                    '</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            figure_1  = st.file_uploader("Figure 1", type=C.ALLOWED_IMAGE_TYPES, key="f1")
            caption_1 = st.text_area(f"Caption 1 (max {C.CAPTION_MAX_WORDS} words)", height=68,
                                       placeholder="Describe Figure 1")
            c1_w = _wc(caption_1)
            st.markdown(_wc_line(c1_w, C.CAPTION_MAX_WORDS), unsafe_allow_html=True)
            
        with fc2:
            figure_2  = st.file_uploader("Figure 2", type=C.ALLOWED_IMAGE_TYPES, key="f2")
            caption_2 = st.text_area(f"Caption 2 (max {C.CAPTION_MAX_WORDS} words)", height=68,
                                       placeholder="Describe Figure 2")
            c2_w = _wc(caption_2)
            st.markdown(_wc_line(c2_w, C.CAPTION_MAX_WORDS), unsafe_allow_html=True)

    # ── Submit button ─────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    submitted = st.button("🚀 Validate & Generate Reports",
                           use_container_width=True, type="primary")

# ════════════════════════════════════════════════════════════════════════════
#  RIGHT COLUMN — live document preview
# ════════════════════════════════════════════════════════════════════════════
with right:
    # Build preview variables safely
    _name    = _esc(student_name)   if 'student_name'     in dir() else ""
    _topic   = _esc(research_topic) if 'research_topic'   in dir() else ""
    _prog    = _esc(graduate_program) if 'graduate_program' in dir() else ""
    _deg     = _esc(degree)         if 'degree'           in dir() else ""
    _yr      = _esc(year)           if 'year'             in dir() else ""
    _email   = _esc(contact_email)  if 'contact_email'    in dir() else ""
    _adv     = _esc(advisor)        if 'advisor'          in dir() else ""
    _goal    = _esc(career_goal)    if 'career_goal'      in dir() else ""
    _sp      = _esc(sponsor)        if 'sponsor'          in dir() else ""
    _p1      = _esc(abstract_p1)    if 'abstract_p1'      in dir() else ""
    _p2      = _esc(abstract_p2)    if 'abstract_p2'      in dir() else ""

    # word count badge for preview header
    if is_two_paragraphs:
        wc_total = _wc(abstract_p1) + _wc(abstract_p2 or "")
        wc_limit = C.ABSTRACT_MAX_WORDS_TOTAL
    elif is_figures:
        wc_total = _wc(abstract_p1)
        wc_limit = 200
    else:
        wc_total = _wc(abstract_p1)
        wc_limit = C.ABSTRACT_MAX_WORDS_TOTAL

    badge_html = _badge(wc_total, wc_limit)

    # sponsor row
    sp_row = f'<div><span class="doc-label">Sponsor:</span> {_sp}</div>' if _sp else ""

    # paragraph block
    _p1_fallback = '<em style="color:#aaa">Abstract will appear here...</em>'
    p1_block = f'<div class="doc-para">{_p1 if _p1 else _p1_fallback}</div>'
    p2_block = f'<div class="doc-para">{_p2}</div>' if _p2 else ""

    # figures block
    if is_figures and (figure_1 or figure_2):
        if figure_1 and figure_2:
            figs_html = """
            <div class="fig-row">
              <div class="fig-col">
                <div style="background:#e8ecf0;height:80px;border:1px solid #bbb;
                            display:flex;align-items:center;justify-content:center;
                            font-size:9px;color:#888">Figure 1</div>
                <div class="fig-cap">""" + _esc(caption_1 or "") + """</div>
              </div>
              <div class="fig-col">
                <div style="background:#e8ecf0;height:80px;border:1px solid #bbb;
                            display:flex;align-items:center;justify-content:center;
                            font-size:9px;color:#888">Figure 2</div>
                <div class="fig-cap">""" + _esc(caption_2 or "") + """</div>
              </div>
            </div>"""
        else:
            cap = _esc(caption_1 or caption_2 or "")
            figs_html = """
            <div style="text-align:center;margin-top:10px">
              <div style="background:#e8ecf0;height:90px;border:1px solid #bbb;
                          display:inline-block;width:55%;
                          display:flex;align-items:center;justify-content:center;
                          font-size:9px;color:#888">Figure</div>
              <div class="fig-cap" style="text-align:center;margin-top:3px">""" + cap + """</div>
            </div>"""
    else:
        figs_html = ""

    preview_html = f"""
    <div class="preview-wrap">
      <div class="preview-header">📄 Live Preview &nbsp;{badge_html}</div>
      <div class="preview-body">
        <div class="doc-page">
          <div class="header-row">
            <div class="headshot-box">Photo</div>
            <div class="doc-info">
              <div class="doc-name">{_name or "<em style='color:#aaa'>Your Name</em>"}</div>
              <div><span class="doc-label">Research topic:</span> {_topic or "<em style='color:#aaa'>Research topic</em>"}</div>
              {sp_row}
              <div><span class="doc-label">Degree objective:</span> {_deg} {("(" + _yr + ")") if _yr else ""}</div>
              <div><span class="doc-label">Contact:</span> {_email}</div>
              <div><span class="doc-label">Advisor:</span> {_adv}</div>
              <div><span class="doc-label">Career goal:</span> {_goal}</div>
            </div>
          </div>
          <div class="doc-heading">Abstract</div>
          {p1_block}
          {p2_block}
          {figs_html}
        </div>
      </div>
    </div>
    """
    st.html(preview_html)

# ════════════════════════════════════════════════════════════════════════════
#  Post-submit validation & generation
# ════════════════════════════════════════════════════════════════════════════
if submitted:
    errors = []

    required = {
        "Full Name": student_name, "Graduate Program": graduate_program,
        "Graduation Year": year, "Contact Email": contact_email,
        "Advisor": advisor, "Research Topic": research_topic,
        "Abstract": abstract_p1,
    }
    if is_two_paragraphs:
        required["Abstract Paragraph 2"] = abstract_p2

    for label, val in required.items():
        if not val or not val.strip():
            errors.append(f"**{label}** is required.")

    p1w = _wc(abstract_p1)
    p2w = _wc(abstract_p2 or "")
    total_w = p1w + p2w

    if is_two_paragraphs:
        if p1w > C.ABSTRACT_MAX_WORDS_P1:
            errors.append(f"**Paragraph 1** exceeds {C.ABSTRACT_MAX_WORDS_P1} words ({p1w} used).")
        if total_w > C.ABSTRACT_MAX_WORDS_TOTAL:
            errors.append(f"**Total abstract** exceeds {C.ABSTRACT_MAX_WORDS_TOTAL} words ({total_w} used).")
    elif is_figures:
        if p1w > 200:
            errors.append(f"**Abstract** exceeds 200 words ({p1w} used).")
    else:
        if p1w > C.ABSTRACT_MAX_WORDS_TOTAL:
            errors.append(f"**Abstract** exceeds {C.ABSTRACT_MAX_WORDS_TOTAL} words ({p1w} used).")

    topic_w = _wc(research_topic)
    if topic_w > C.RESEARCH_TOPIC_MAX_WORDS:
        errors.append(f"**Research Topic** exceeds {C.RESEARCH_TOPIC_MAX_WORDS} words ({topic_w} used).")
        
    c1_w = _wc(caption_1)
    if c1_w > C.CAPTION_MAX_WORDS:
        errors.append(f"**Caption 1** exceeds {C.CAPTION_MAX_WORDS} words ({c1_w} used).")
        
    c2_w = _wc(caption_2)
    if c2_w > C.CAPTION_MAX_WORDS:
        errors.append(f"**Caption 2** exceeds {C.CAPTION_MAX_WORDS} words ({c2_w} used).")

    if contact_email and not _validate_email(contact_email):
        errors.append("Please enter a valid **email address**.")
    if year and (not year.strip().isdigit() or len(year.strip()) != 4):
        errors.append("**Graduation Year** must be 4 digits.")
    if not headshot:
        errors.append("**Headshot** is required.")
    elif _file_too_large(headshot):
        errors.append(f"**Headshot** exceeds {C.MAX_IMAGE_SIZE_MB} MB.")
    if _file_too_large(figure_1):
        errors.append(f"**Figure 1** exceeds {C.MAX_IMAGE_SIZE_MB} MB.")
    if _file_too_large(figure_2):
        errors.append(f"**Figure 2** exceeds {C.MAX_IMAGE_SIZE_MB} MB.")
    if figure_1 and not (caption_1 and caption_1.strip()):
        errors.append("Provide a **caption for Figure 1**.")
    if figure_2 and not (caption_2 and caption_2.strip()):
        errors.append("Provide a **caption for Figure 2**.")

    if errors:
        with left:
            for e in errors:
                st.error(e)
    else:
        with left:
            with st.spinner("Generating reports…"):
                data = {
                    "student_name":    student_name.strip(),
                    "graduate_program": graduate_program.strip(),
                    "research_topic":  research_topic.strip(),
                    "sponsor":         (sponsor or "").strip(),
                    "degree":          degree,
                    "year":            year.strip(),
                    "contact_email":   contact_email.strip(),
                    "advisor":         advisor.strip(),
                    "career_goal":     career_goal,
                    "headshot":        headshot,
                    "abstract_p1":     abstract_p1.strip(),
                    "abstract_p2":     (abstract_p2 or "").strip(),
                    "figure_1":        figure_1,
                    "caption_1":       (caption_1 or "").strip(),
                    "figure_2":        figure_2,
                    "caption_2":       (caption_2 or "").strip(),
                }
                try:
                    from latex_generator import generate_pdf
                    try:
                        pdf_io = generate_pdf(data)
                    except ValueError as ve:
                        if "exceeds 1 page" in str(ve):
                            st.error("❌ **Page limit exceeded.** Please shorten your text or figures so everything fits on one page.")
                            st.stop()
                        else:
                            raise

                    doc_io = generate_docx(data)

                    parts     = student_name.strip().split()
                    last      = parts[-1] if parts else "Unknown"
                    first     = parts[0]  if len(parts) > 1 else ""
                    prog      = graduate_program.strip().replace(" ", "")
                    base_name = f"GS26_{last}_{first}_{prog}"

                    st.success("✅ Reports ready! Download below.")
                    d1, d2 = st.columns(2)
                    with d1:
                        st.download_button("📄 Download DOCX", data=doc_io.getvalue(),
                            file_name=f"{base_name}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True)
                    with d2:
                        st.download_button("📕 Download PDF", data=pdf_io.getvalue(),
                            file_name=f"{base_name}.pdf",
                            mime="application/pdf",
                            use_container_width=True)

                except Exception as exc:
                    st.error(f"Error generating reports: {exc}")
