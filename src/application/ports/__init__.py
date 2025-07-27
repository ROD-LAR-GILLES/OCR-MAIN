# application/ports/__init__.py
"""
Puertos para arquitectura hexagonal.
"""
from .ocr_port import OCRPort
from .table_extractor_port import TableExtractorPort
from .storage_port import StoragePort

__all__ = ['OCRPort', 'TableExtractorPort', 'StoragePort']
