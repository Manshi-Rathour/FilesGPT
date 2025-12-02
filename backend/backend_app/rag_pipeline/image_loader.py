import os
import platform
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# ---------- OS-Specific Setup ----------
system_name = platform.system()

# Configure Tesseract path for Windows only
if system_name == "Windows":
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        raise FileNotFoundError(
            f"Tesseract not found at {tesseract_path}. Please verify the installation path."
        )

    # Configure Poppler path (required for pdf2image)
    POPPLER_PATH = r"D:\downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin"
else:
    # macOS / Linux (usually already in PATH)
    POPPLER_PATH = None

# ---------- Directory Setup ----------
UPLOAD_DIR = "backend_app/rag_pipeline/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Text Extraction Functions ----------
def extract_text_from_image_file(file_path: str) -> str:
    """Extract text from a single image file (PNG, JPG, JPEG)."""
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    text = text.strip()

    print("\n=== Extracted Text ===\n")
    print(text)

    return text


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes by converting pages to images first."""
    text = ""

    # Pass poppler_path only if set
    pages = (
        convert_from_bytes(pdf_bytes, poppler_path=POPPLER_PATH)
        if POPPLER_PATH
        else convert_from_bytes(pdf_bytes)
    )

    for page_num, page in enumerate(pages, start=1):
        temp_path = os.path.join(UPLOAD_DIR, f"temp_page_{page_num}.png")
        page.save(temp_path, "PNG")
        text += extract_text_from_image_file(temp_path) + "\n"
        os.remove(temp_path)

    text = text.strip()

    print("\n=== Extracted Text ===\n")
    print(text)

    return text
