from typing import Dict, Optional
from .base_driver import BaseDriver

class BinaryDriver(BaseDriver):
    """Fallback para qualquer arquivo desconhecido ou executáveis."""
    SUPPORTED_EXTENSIONS = [".exe", ".dll", ".bin", ".iso"]
    SUPPORTED_MIMES = ["application/octet-stream", "application/x-msdownload"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        return "Arquivo binário genérico."

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        return {"driver": "binary_driver"}
