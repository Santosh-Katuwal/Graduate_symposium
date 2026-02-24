"""
latex_generator.py — Generates a compiled PDF and a LaTeX ZIP using the 
provided exact Template.tex structure but customized.
"""

import io
import os
import zipfile
import subprocess
import shutil
import tempfile
from jinja2 import Environment, BaseLoader

import config as C

# Escape latex special chars
def escape_latex(text: str) -> str:
    if not text:
        return ""
    # Very basic escaping to prevent latex compilation errors
    replacements = {
        "\\": "\\textbackslash{}",
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
    }
    escaped = "".join(replacements.get(c, c) for c in text)
    # Convert newlines to latex newlines
    return escaped.replace("\n", "\\\\")

# The Jinja2 Template (matches exactly Template.tex but with variables)
LATEX_TEMPLATE = r"""\documentclass[12pt]{article}

% Font and formatting packages
\usepackage[T1]{fontenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault} % Arial format, 12 pt.
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\usepackage[skip=6pt, parfill]{parskip} % Single spacing 6 pt. No indentation.
\usepackage{caption}

% Set figure caption styling to match template requirements
\captionsetup[figure]{font={sf,it,normalsize}, labelsep=period, justification=raggedright, singlelinecheck=false}

\begin{document}

% --- Header Section (Fixed for No Overlap) ---
\noindent
\begin{minipage}[t]{2in} % Fixed 2-inch width for the headshot
    \vspace{0pt} 
    {% if headshot_filename %}
    \includegraphics[width=2in, height=2in, keepaspectratio]{ {{headshot_filename}} } 
    {% else %}
    [No Headshot]
    {% endif %}
\end{minipage}%
\hspace{0.2in} % Explicit gutter to prevent text from touching the photo
\begin{minipage}[t]{\dimexpr\textwidth-2.2in\relax} % Dynamic remaining width
    \vspace{0pt}
    \raggedright % Ensures text doesn't stretch awkwardly
    {\large \textbf{ {{student_name}} }}\\[8pt]
    \textbf{Research topic:} {{research_topic}}\\[2pt]
    {% if sponsor %}
    \textbf{Sponsor:} {{sponsor}}\\[2pt]
    {% endif %}
    \textbf{Degree objective:} {{degree}} ({{year}})\\[2pt]
    \textbf{Contact:} {{contact_email}}\\[2pt]
    \textbf{Advisor:} {{advisor}}\\[2pt]
    \textbf{Career goal:} {{career_goal}}
\end{minipage}

\vspace{30pt}

% --- Abstract Section ---
{\large \textbf{Abstract}}

{{abstract_p1}}
{% if abstract_p2 %}

{{abstract_p2}}
{% endif %}
{% if figure_1_filename or figure_2_filename %}

\vspace{30pt}

% --- Figures Section ---
\begin{figure}[htbp]
    \centering
    {% if figure_1_filename and figure_2_filename %}
    % Two Column Layout
    \begin{minipage}[t]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth, height=2.2in, keepaspectratio]{ {{figure_1_filename}} }
        \caption{ {{caption_1}} }
    \end{minipage}
    \hfill
    \begin{minipage}[t]{0.48\textwidth}
        \centering
        \includegraphics[width=\textwidth, height=2.2in, keepaspectratio]{ {{figure_2_filename}} }
        \caption{ {{caption_2}} }
    \end{minipage}
    {% else %}
    % One Column Layout
    {% if figure_1_filename %}
    \includegraphics[width=0.6\textwidth, height=2.7in, keepaspectratio]{ {{figure_1_filename}} }
    \caption{ {{caption_1}} }
    {% endif %}
    {% if figure_2_filename %}
    \includegraphics[width=0.6\textwidth, height=2.7in, keepaspectratio]{ {{figure_2_filename}} }
    \caption{ {{caption_2}} }
    {% endif %}
    {% endif %}
\end{figure}
{% endif %}

\end{document}
"""


def _generate_latex_source(data: dict) -> str:
    """Uses Jinja2 to populate the LaTeX template with the user's data"""
    env = Environment(loader=BaseLoader())
    template = env.from_string(LATEX_TEMPLATE)

    # Determine filenames if images are present
    context = {
        "student_name": escape_latex(data.get("student_name", "")),
        "research_topic": escape_latex(data.get("research_topic", "")),
        "sponsor": escape_latex(data.get("sponsor", "")),
        "degree": escape_latex(data.get("degree", "")),
        "year": escape_latex(data.get("year", "")),
        "contact_email": escape_latex(data.get("contact_email", "")),
        "advisor": escape_latex(data.get("advisor", "")),
        "career_goal": escape_latex(data.get("career_goal", "")),
        "abstract_p1": escape_latex(data.get("abstract_p1", "")),
        "abstract_p2": escape_latex(data.get("abstract_p2", "")),
        "caption_1": escape_latex(data.get("caption_1", "")),
        "caption_2": escape_latex(data.get("caption_2", "")),
        "headshot_filename": "headshot.png" if data.get("headshot") else None,
        "figure_1_filename": "figure1.png" if data.get("figure_1") else None,
        "figure_2_filename": "figure2.png" if data.get("figure_2") else None,
    }

    return template.render(**context)

def _save_image_to_disk(uploaded_file, filepath):
    """Saves a streamlit UploadedFile to disk."""
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getvalue())

def generate_pdf(data: dict) -> io.BytesIO:
    """Generates a PDF using pdflatex. Returns a BytesIO object of the PDF."""
    tex_content = _generate_latex_source(data)

    # Work inside a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        tex_path = os.path.join(temp_dir, "main.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)

        if data.get("headshot"):
            _save_image_to_disk(data["headshot"], os.path.join(temp_dir, "headshot.png"))
        if data.get("figure_1"):
            _save_image_to_disk(data["figure_1"], os.path.join(temp_dir, "figure1.png"))
        if data.get("figure_2"):
            _save_image_to_disk(data["figure_2"], os.path.join(temp_dir, "figure2.png"))

        # Compile twice to resolve references/layout properly
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            check=False
        )
        
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            check=False
        )

        import re
        # Look for "Output written on main.pdf (X pages"
        match = re.search(r"Output written on main\.pdf \((\d+)\s+page", result.stdout)
        if match:
            pages = int(match.group(1))
            if pages > 1:
                raise ValueError("Submission exceeds 1 page limit.")

        pdf_path = os.path.join(temp_dir, "main.pdf")
        if not os.path.exists(pdf_path):
            raise RuntimeError(f"PDF failed to generate. LaTeX Log: {result.stdout}")

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        return io.BytesIO(pdf_bytes)
    finally:
        shutil.rmtree(temp_dir)

def generate_latex_zip(data: dict) -> io.BytesIO:
    """Generates a ZIP file in memory containing the latex source and images."""
    tex_content = _generate_latex_source(data)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("main.tex", tex_content)
        
        if data.get("headshot"):
            zip_file.writestr("headshot.png", data["headshot"].getvalue())
        if data.get("figure_1"):
            zip_file.writestr("figure1.png", data["figure_1"].getvalue())
        if data.get("figure_2"):
            zip_file.writestr("figure2.png", data["figure_2"].getvalue())

    zip_buffer.seek(0)
    return zip_buffer
