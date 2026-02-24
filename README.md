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



