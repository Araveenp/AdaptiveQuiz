"""Utility services: PDF extraction, image OCR, text processing."""
import os


def extract_text_from_pdf(file_obj, upload_folder="/tmp/uploads"):
    """Extract text from an uploaded PDF file."""
    try:
        import pypdf
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, file_obj.filename)
        file_obj.save(path)

        reader = pypdf.PdfReader(path)
        text = " ".join(
            [page.extract_text() for page in reader.pages if page.extract_text()]
        )
        try:
            os.remove(path)
        except OSError:
            pass
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def extract_text_from_image(file_obj):
    """Extract text from an image — lightweight fallback without Pillow."""
    try:
        # Try PIL if available locally (not bundled for Vercel)
        from PIL import Image
        img = Image.open(file_obj)
        try:
            import pytesseract
            text = pytesseract.image_to_string(img)
            return text.strip() if text else ""
        except ImportError:
            return "[Image uploaded — OCR requires pytesseract]"
    except ImportError:
        return "[Image OCR not available — please use PDF or text input instead]"
    except Exception as e:
        print(f"Image extraction error: {e}")
        return ""


def clean_text(text):
    """Clean and normalize extracted text."""
    if not text:
        return ""
    import re
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()
