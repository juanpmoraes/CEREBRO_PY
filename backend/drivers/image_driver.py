from typing import Dict, Optional
from .base_driver import BaseDriver
import io
import os

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

class ImageDriver(BaseDriver):
    SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    SUPPORTED_MIMES = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    def extract_summary(self, file_path: str, content: Optional[bytes] = None) -> str:
        return "Arquivo de imagem."

    def extract_metadata(self, file_path: str, content: Optional[bytes] = None) -> Dict:
        meta = {"driver": "image_driver"}
        if PILLOW_AVAILABLE and content:
            try:
                img = Image.open(io.BytesIO(content))
                meta["format"] = img.format
                meta["size"] = img.size
                meta["mode"] = img.mode
            except:
                pass
        return meta

    def generate_thumbnail(self, file_path: str, out_path: str) -> bool:
        if not PILLOW_AVAILABLE or not os.path.exists(file_path):
            return False
        try:
            img = Image.open(file_path)
            img.thumbnail((256, 256))
            img.save(out_path)
            return True
        except:
            return False
