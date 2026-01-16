
import os
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

def extract_text_from_pdf(pdf_path):
    if not PdfReader:
        # Fallback or error if pypdf not available
        return ""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def load_resume_text(path):
    if path.lower().endswith('.pdf'):
        return extract_text_from_pdf(path)
    else:
        # Assume text/md
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
