"""
Text extraction service supporting PDF, DOCX, and TXT formats.
Uses PyMuPDF for PDF and python-docx for DOCX as specified in Chapter 3.
"""
import re
import io
from typing import Tuple


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import fitz  # PyMuPDF
    text_parts = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return _clean_text("\n".join(text_parts))


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
