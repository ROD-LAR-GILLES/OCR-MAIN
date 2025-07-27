"""
Métricas de procesamiento OCR - Entidad pura de dominio.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ProcessingMetrics:
    """Métricas de procesamiento OCR sin dependencias externas."""
    page_number: Optional[int] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    image_quality_score: float = 0.0
    preprocessing_applied: bool = False
    metrics_data: Dict[str, Any] = field(default_factory=dict)
    total_processing_time: float = 0.0
    average_confidence: float = 0.0
    document_quality: Dict[str, Any] = field(default_factory=dict)
    
    def add_page_metrics(self, page_metrics: 'ProcessingMetrics') -> None:
        """Acumula métricas de una página al total del documento."""
        self.total_processing_time += page_metrics.processing_time
        
        if self.average_confidence == 0.0:
            self.average_confidence = page_metrics.confidence_score
        else:
            self.average_confidence = (self.average_confidence + page_metrics.confidence_score) / 2
    
    def is_high_quality(self) -> bool:
        """Determina si las métricas indican alta calidad."""
        from domain.constants import HIGH_QUALITY_THRESHOLD
        return self.confidence_score >= HIGH_QUALITY_THRESHOLD