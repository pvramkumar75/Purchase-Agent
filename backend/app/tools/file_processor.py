import os
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
from app.tools.ocr import ocr_tool
from typing import Optional, Dict, Any

class FileProcessor:
    @staticmethod
    def read_pdf(file_path: str) -> str:
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            if len(text.strip()) < 50: # Likely scanned
                # In production, we'd use pdf2image here
                return "PDF appears to be scanned. OCR required."
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    @staticmethod
    def read_docx(file_path: str) -> str:
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    @staticmethod
    def read_excel(file_path: str) -> str:
        try:
            df = pd.read_excel(file_path)
            # Convert to markdown for LLM to understand structure easily
            return df.to_markdown()
        except Exception as e:
            return f"Error reading Excel: {str(e)}"

    @staticmethod
    def read_file(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf': return FileProcessor.read_pdf(file_path)
        if ext in ['.xlsx', '.xls']: return FileProcessor.read_excel(file_path)
        if ext == '.docx': return FileProcessor.read_docx(file_path)
        if ext in ['.jpg', '.jpeg', '.png']: return ocr_tool.extract_text(file_path)
        if ext in ['.txt', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return "Unsupported file format."

    @staticmethod
    def detect_document_type(content: str) -> str:
        # Keywords based detection
        content_lower = content.lower()
        if "quotation" in content_lower or "quote" in content_lower or "proforma" in content_lower:
            return "Quotation"
        if "purchase order" in content_lower or "po #" in content_lower:
            return "Purchase Order"
        if "request for quotation" in content_lower or "rfq" in content_lower:
            return "RFQ"
        if "invoice" in content_lower:
            return "Invoice"
        return "Unknown"

file_processor = FileProcessor()
