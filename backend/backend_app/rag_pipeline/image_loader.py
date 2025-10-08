import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes

UPLOAD_DIR = "backend_app/rag_pipeline/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_image_file(file_path: str) -> str:
    """
    Extracts text from a single image file (PNG, JPG, JPEG).
    Returns extracted text as a string.
    """
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text.strip()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF by converting pages to images first.
    Useful if you want to support PDF via the image loader.
    """
    text = ""
    pages = convert_from_bytes(pdf_bytes)
    for page_num, page in enumerate(pages, start=1):
        temp_path = os.path.join(UPLOAD_DIR, f"temp_page_{page_num}.png")
        page.save(temp_path, "PNG")
        text += extract_text_from_image_file(temp_path) + "\n"
        os.remove(temp_path)
    return text.strip()
