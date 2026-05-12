from typing import Dict, Optional
from .base_driver import BaseDriver
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

class CodeDriver(BaseDriver):
    SUPPORTED_EXTENSIONS = [".py", ".js", ".ts", ".rs", ".go", ".c", ".cpp", ".h", ".java", ".php", ".rb"]
    SUPPORTED_MIMES = ["text/x-python", "application/javascript", "text/javascript"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        if content:
            return content.decode('utf-8', errors='ignore')[:10000]
        return ""

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        meta = {"driver": "code_driver"}
        if PYGMENTS_AVAILABLE and content:
            try:
                lexer = get_lexer_for_filename(file_path)
                meta["language"] = lexer.name
            except:
                meta["language"] = "unknown"
        return meta
