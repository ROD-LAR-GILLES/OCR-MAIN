# application/ports.py
"""
Puertos (interfaces) para arquitectura hexagonal - Módulo de compatibilidad.
Importa desde los módulos individuales para mantener compatibilidad hacia atrás.
"""
from .ports.ocr_port import OCRPort
from .ports.table_extractor_port import TableExtractorPort
from .ports.storage_port import StoragePort

__all__ = ['OCRPort', 'TableExtractorPort', 'StoragePort']