"""
Puertos del dominio para la arquitectura hexagonal.

Estos puertos definen las interfaces que deben implementar
los adaptadores para interactuar con el dominio.
"""

from .ocr_port import OCRPort
from .table_extractor_port import TableExtractorPort
from .storage_port import StoragePort

__all__ = [
    'OCRPort',
    'TableExtractorPort',
    'StoragePort',
]