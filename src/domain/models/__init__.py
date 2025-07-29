"""
Modelos del dominio OCR.
"""
from .document import Document
from .ocr_result import OCRResult
from .processing_metrics import ProcessingMetrics

__all__ = ['Document', 'OCRResult', 'ProcessingMetrics']