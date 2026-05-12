from typing import Dict, Optional
from .base_driver import BaseDriver
import io

try:
    import openpyxl
    import docx
    OFFICE_LIBS_AVAILABLE = True
except ImportError:
    OFFICE_LIBS_AVAILABLE = False

class OfficeDriver(BaseDriver):
    SUPPORTED_EXTENSIONS = [".xlsx", ".xls", ".docx"]
    SUPPORTED_MIMES = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        if not OFFICE_LIBS_AVAILABLE or not content:
            return "Office Driver libraries not installed."
        
        text = ""
        try:
            if file_path.endswith('.docx'):
                doc = docx.Document(io.BytesIO(content))
                text = "\n".join([para.text for para in doc.paragraphs])
            elif file_path.endswith('.xlsx'):
                wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
                for sheet in wb.worksheets:
                    for row in sheet.iter_rows(values_only=True):
                        text += " ".join([str(c) for c in row if c is not None]) + " "
                        if len(text) > 5000: break
                    if len(text) > 5000: break
        except:
            text = "Erro ao processar arquivo Office."
        return text[:5000]

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        return {"driver": "office_driver"}
