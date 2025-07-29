"""
Modelos de dominio - ARCHIVO DE COMPATIBILIDAD.
Este archivo mantiene la compatibilidad mientras migramos.
"""
# Importar desde la nueva estructura
from domain.models.processing_metrics import ProcessingMetrics as NewProcessingMetrics
from domain.models.ocr_result import OCRResult as NewOCRResult

# Crear alias para mantener compatibilidad
ProcessingMetrics = NewProcessingMetrics
OCRResult = NewOCRResult

# Mantener las clases existentes por compatibilidad
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional

@dataclass
class Document:
    """Documento procesado - mantenido por compatibilidad."""
    name: str
    source_path: str
    extracted_text: str = ""
    tables: list = field(default_factory=list)

# Re-exportar todo
__all__ = ['ProcessingMetrics', 'OCRResult', 'Document']