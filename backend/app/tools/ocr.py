import pytesseract
from PIL import Image
import os

class OCRTool:
    def __init__(self):
        # Tesseract is assumed to be installed in the Docker image
        pass

    def extract_text(self, image_path: str) -> str:
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"OCR Error: {str(e)}"

    def extract_from_pdf_scanned(self, pdf_path: str) -> str:
        # Placeholder for complex multi-page PDF OCR
        # Usually requires pdf2image to convert pages to images first
        return "Scanned PDF OCR not yet fully implemented. Requires pdf2image."

ocr_tool = OCRTool()
