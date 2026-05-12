from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseDriver(ABC):
    SUPPORTED_EXTENSIONS: List[str] = []
    SUPPORTED_MIMES: List[str] = []

    @abstractmethod
    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        """Extrai texto para busca full-text."""
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        """Extrai metadados específicos do tipo."""
        pass

    def generate_thumbnail(self, file_path: str, out_path: str) -> bool:
        """Gera thumbnail se aplicável. Retorna True se sucesso."""
        return False
