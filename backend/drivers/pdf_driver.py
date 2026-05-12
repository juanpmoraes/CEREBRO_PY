from typing import Dict, Optional
from .base_driver import BaseDriver
import os

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class PDFDriver(BaseDriver):
    SUPPORTED_EXTENSIONS = [".pdf"]
    SUPPORTED_MIMES = ["application/pdf"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        if not PYMUPDF_AVAILABLE:
            return "PDF Driver (fitz) not installed."
        
        text = ""
        try:
            # Se tivermos o path físico, melhor. Se não, usamos o stream se suportado.
            # PyMuPDF suporta stream.
            if content:
                doc = fitz.open(stream=content, filetype="pdf")
                for page in doc:
                    text += page.get_text()
                    if len(text) > 5000: break
                doc.close()
        except Exception as e:
            text = f"Erro ao extrair PDF: {str(e)}"
        return text

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        meta = {"driver": "pdf_driver"}
        if PYMUPDF_AVAILABLE and content:
            try:
                doc = fitz.open(stream=content, filetype="pdf")
                meta["pages"] = doc.page_count
                meta["metadata"] = doc.metadata
                doc.close()
            except:
                pass
        return meta

    def generate_thumbnail(self, file_path: str, out_path: str) -> bool:
        if not PYMUPDF_AVAILABLE or not os.path.exists(file_path):
            return False
        try:
            doc = fitz.open(file_path)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            pix.save(out_path)
            doc.close()
            return True
        except:
            return False
