"""
Resultado de OCR - Entidad de dominio.
"""
from dataclasses import dataclass
from .processing_metrics import ProcessingMetrics


@dataclass
class OCRResult:
    """Resultado de OCR con métricas de calidad."""
    text: str
    metrics: ProcessingMetrics
    page_count: int
    processing_time: float
    
    @property
    def quality_score(self) -> float:
        """Puntuación de calidad general del resultado."""
        return self.metrics.average_confidence
    
    @property
    def is_high_quality(self) -> bool:
        """Indica si el resultado es de alta calidad."""
        return self.quality_score >= 80.0