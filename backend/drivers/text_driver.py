from typing import Dict, Optional
from .base_driver import BaseDriver

class TextDriver(BaseDriver):
    SUPPORTED_EXTENSIONS = [".txt", ".md", ".csv", ".json", ".yaml", ".xml"]
    SUPPORTED_MIMES = ["text/plain", "text/markdown", "application/json", "text/csv"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        if content:
            return content.decode('utf-8', errors='ignore')[:5000] # Limite para o banco
        return ""

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        return {
            "driver": "text_driver",
            "char_count": len(content) if content else 0
        }
