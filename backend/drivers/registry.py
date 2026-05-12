from typing import Optional
from .base_driver import BaseDriver
from .text_driver import TextDriver
from .code_driver import CodeDriver
from .pdf_driver import PDFDriver
from .image_driver import ImageDriver
from .office_driver import OfficeDriver
from .archive_driver import ArchiveDriver
from .binary_driver import BinaryDriver
from .value_driver import ValueDriver

DRIVERS = [
    TextDriver(),
    CodeDriver(),
    PDFDriver(),
    ImageDriver(),
    OfficeDriver(),
    ArchiveDriver(),
    BinaryDriver(),
    ValueDriver()
]

def get_driver(mime_type: Optional[str] = None, file_ext: Optional[str] = None) -> BaseDriver:
    """Retorna o driver mais adequado para o tipo de arquivo."""
    # Tenta MIME primeiro
    if mime_type:
        for driver in DRIVERS:
            if mime_type in driver.SUPPORTED_MIMES:
                return driver
    
    # Tenta extensão
    if file_ext:
        ext = file_ext.lower() if file_ext.startswith('.') else f".{file_ext.lower()}"
        for driver in DRIVERS:
            if ext in driver.SUPPORTED_EXTENSIONS:
                return driver
                
    # Fallback para BinaryDriver
    return DRIVERS[6] # BinaryDriver
