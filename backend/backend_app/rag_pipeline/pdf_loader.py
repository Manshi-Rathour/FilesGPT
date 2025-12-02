import os
import fitz
import requests
from bs4 import BeautifulSoup
from typing import Tuple

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n\n".join(pages).strip()

def download_file_from_url(url: str, dest_path: str, timeout: int = 15) -> Tuple[str, str]:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(resp.content)
    return content_type, dest_path

def extract_text_from_url_maybe_html(file_path: str, content_type: str) -> str:
    # Determine if PDF
    if "application/pdf" in content_type.lower() or file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
        print("\n=== Final Extracted Text ===\n")
        print(text)
        return text

    try:
        # Try HTML parsing
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.extract()
        text = "\n".join([line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()])

        print("\n=== Extracted Text ===\n")
        print(text)
        return text

    except Exception:
        # Fallback to PDF parse
        try:
            text = extract_text_from_pdf(file_path)
            print("\n=== Extracted Text ===\n")
            print(text)
            return text
        except Exception:
            print("\n=== Extracted Text ===\n")
            print("")  # empty string
            return ""
