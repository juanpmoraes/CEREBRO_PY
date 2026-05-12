import zipfile
import tarfile
import io
from typing import Dict, Optional
from .base_driver import BaseDriver

class ArchiveDriver(BaseDriver):
    SUPPORTED_EXTENSIONS = [".zip", ".tar", ".gz", ".7z"]
    SUPPORTED_MIMES = ["application/zip", "application/x-tar", "application/x-gzip"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        if not content: return ""
        files = []
        try:
            if zipfile.is_zipfile(io.BytesIO(content)):
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    files = z.namelist()
        except:
            pass
        return "Arquivo comprimido. Conteúdo: " + ", ".join(files[:20])

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        return {"driver": "archive_driver"}
