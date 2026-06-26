"""
Text extraction service supporting PDF, DOCX, and TXT formats.
Uses pypdf/pdfplumber for PDF (pure-Python, no C build required) and
python-docx for DOCX as specified in Chapter 3.
"""
import re
import io
from typing import Tuple


def extract_text_from_pdf(file_bytes: bytes) -> str:
    # Try pdfplumber first (better layout handling), fall back to pypdf
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return _clean_text("\n".join(pages))
    except Exception:
        pass

    # Fallback: pypdf (also pure-Python, no compilation)
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return _clean_text("\n".join(pages))


def extract_text_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return _clean_text("\n".join(paragraphs))


def extract_text_from_txt(file_bytes: bytes) -> str:
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")
    return _clean_text(text)


def extract_text(file_bytes: bytes, file_type: str) -> Tuple[str, int]:
    extractors = {
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
        "txt": extract_text_from_txt,
    }
    extractor = extractors.get(file_type.lower())
    if not extractor:
        raise ValueError(f"Unsupported file type: {file_type}")

    text = extractor(file_bytes)
    word_count = len(text.split())
    return text, word_count


def _clean_text(text: str) -> str:
    # Normalise whitespace and remove encoding artefacts
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()
