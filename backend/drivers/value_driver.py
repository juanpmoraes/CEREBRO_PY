from typing import Dict, Optional
from .base_driver import BaseDriver

class ValueDriver(BaseDriver):
    """Driver para nós que representam valores puros, sem arquivos físicos."""
    
    SUPPORTED_EXTENSIONS = []
    SUPPORTED_MIMES = ["text/plain", "application/json-value"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        if content:
            return content.decode('utf-8', errors='ignore')
        return ""

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        return {
            "driver": "value_driver",
            "is_virtual": True
        }
