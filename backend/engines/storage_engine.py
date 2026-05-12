import os
import hashlib
import aiofiles
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv("VAULT_PATH", "./backend/vault"))
THUMBNAIL_PATH = Path(os.getenv("THUMBNAIL_PATH", "./backend/vault/thumbnails"))

# Garantir que os diretórios existam
VAULT_PATH.mkdir(parents=True, exist_ok=True)
THUMBNAIL_PATH.mkdir(parents=True, exist_ok=True)

class StorageEngine:
    @staticmethod
    async def save_file(file_content: bytes, filename: str) -> str:
        """Salva o arquivo no vault e retorna o path relativo."""
        # Gerar um nome único baseado no conteúdo para evitar duplicatas físicas se desejado
        # Ou apenas usar o filename original. Aqui usaremos o filename para manter clareza.
        file_path = VAULT_PATH / filename
        
        async with aiofiles.open(file_path, mode='wb') as f:
            await f.write(file_content)
        
        return str(file_path.relative_to(VAULT_PATH.parent.parent))

    @staticmethod
    def calculate_hash(content: bytes) -> str:
        """Calcula SHA-256 do conteúdo."""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def get_file_size(content: bytes) -> int:
        """Retorna o tamanho em bytes."""
        return len(content)

    @staticmethod
    def delete_file(relative_path: str):
        """Remove o arquivo físico."""
        full_path = VAULT_PATH.parent.parent / relative_path
        if full_path.exists():
            full_path.unlink()
