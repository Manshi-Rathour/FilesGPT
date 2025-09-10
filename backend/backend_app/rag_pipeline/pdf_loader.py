import os
import fitz
import requests
from bs4 import BeautifulSoup
from typing import Tuple

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    Returns combined text of all pages.
    """
    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        pages.append(page.get_text("text"))
    doc.close()
    return "\n\n".join(pages).strip()

def download_file_from_url(url: str, dest_path: str, timeout: int = 15) -> Tuple[str, str]:
    """
    Downloads the URL to dest_path. Returns (content_type, saved_path).
    If content-type is HTML (text/html) this will save HTML contents into dest_path too.
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "")
    # Ensure destination dir exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    # write binary (works for PDF) or text (HTML) - keep binary, we'll decode for HTML if needed
    with open(dest_path, "wb") as f:
        f.write(resp.content)
    return content_type, dest_path

def extract_text_from_url_maybe_html(file_path: str, content_type: str) -> str:
    """
    If the downloaded file is a PDF (application/pdf), call extract_text_from_pdf.
    If it's HTML (text/html) attempt to extract cleaned text using BeautifulSoup.
    """
    if "application/pdf" in content_type.lower() or file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    else:
        # fallback: try to read file as text and extract HTML text
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            soup = BeautifulSoup(html, "html.parser")
            # remove scripts/styles
            for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
                tag.extract()
            text = soup.get_text(separator="\n")
            # collapse multiple newlines
            text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
            return text
        except Exception:
            # final fallback: try to use pdf extraction anyway
            try:
                return extract_text_from_pdf(file_path)
            except Exception:
                return ""
