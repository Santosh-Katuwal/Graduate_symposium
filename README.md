# Graduate Student Symposium Submission App

A Streamlit-based web application for collecting and formatting student symposium submissions. The app enforces a strict one-page document limit and provides real-time previews for three different layout options.

## Features

- **Three Layout Options**:
  - Text only (Single paragraph) - Max 300 words.
  - Two paragraphs - Max 300 words total (P1 max 200).
  - One paragraph + Figure(s) - Max 200 words + up to 2 figures.
- **Real-time Preview**: A dual-pane interface with a live-updating document preview as you type.
- **Strict One-Page Enforcement**: Uses an internal LaTeX (pdflatex) compilation check to ensure submissions fit on exactly one page before allowing downloads.
- **Multi-format Export**: Generates both professional Word (DOCX) and PDF documents.
- **Image Handling**: Automatically scales headshots and figures to maintain aspect ratio while fitting the page constraints. Supports high-resolution images up to 10MB.

## Local Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd GSA-Symposium
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install LaTeX**:
   You must have `pdflatex` installed on your system and available in your PATH.
   - **Windows**: [MiKTeX](https://miktex.org/)
   - **macOS**: [MacTeX](https://www.tug.org/mactex/)
   - **Linux**: `sudo apt-get install texlive-latex-base texlive-latex-extra`

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Deployment

### Streamlit Cloud
This repository contains a `packages.txt` file and a `requirements.txt` file, making it ready for deployment on [Streamlit Cloud](https://streamlit.io/cloud). The `packages.txt` ensures that the necessary LaTeX binaries are installed on the server.

## Files Structure

- `app.py`: Main Streamlit UI and logic.
- `config.py`: Global constants, word limits, and validation rules.
- `docx_generator.py`: Logic for generating the Word document.
- `latex_generator.py`: Logic for creating the LaTeX source and compiling the PDF.
- `requirements.txt`: Python package dependencies.
- `packages.txt`: System-level dependencies (LaTeX) for cloud deployment.
- `.gitignore`: Rules for ignoring temporary files and caches.
