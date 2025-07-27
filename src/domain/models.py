# domain/models.py
"""
Modelos de dominio para el sistema OCR - Entidades puras sin dependencias externas.
"""
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional


@dataclass
class ProcessingMetrics:
    """Métricas de procesamiento OCR."""
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
        
        # Calcular promedio de confianza (implementación simple)
        if self.average_confidence == 0.0:
            self.average_confidence = page_metrics.confidence_score
        else:
            # Promedio ponderado simple
            self.average_confidence = (self.average_confidence + page_metrics.confidence_score) / 2


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


@dataclass
class Document:
    """Documento procesado con texto y tablas extraídas."""
    
    name: str  # Nombre identificador del documento
    source_path: str  # Ruta al PDF original como string
    extracted_text: str  # Texto extraído por OCR
    tables: List[Any]  # Tablas como DataFrames
    ocr_result: Optional[OCRResult] = None  # Métricas detalladas
    processing_metadata: Dict[str, Any] = field(default_factory=dict)  # Metadatos adicionales
    
    def __post_init__(self) -> None:
        """Validaciones básicas del documento."""
        # Validación: nombre debe ser válido para crear archivos
        if not self.name or not self.name.strip():
            raise ValueError("Document name cannot be empty")
            
        # Validación: texto debe estar inicializado (aunque esté vacío)
        if self.extracted_text is None:
            raise ValueError("Document text cannot be None")
            
        # Validación: lista de tablas debe estar inicializada
        if self.tables is None:
            self.tables = []
            
        # Validación: fuente debe estar definida
        if not self.source_path or not self.source_path.strip():
            raise ValueError("Source path cannot be empty")
    
    @property
    def has_tables(self) -> bool:
        """True si el documento tiene tablas."""
        return len(self.tables) > 0
    
    @property
    def table_count(self) -> int:
        """Número de tablas extraídas."""
        return len(self.tables)
    
    @property
    def word_count(self) -> int:
        """Número de palabras en el texto extraído."""
        return len(self.extracted_text.split()) if self.extracted_text else 0
    
    @property
    def quality_score(self) -> Optional[float]:
        """Puntuación de calidad del OCR (0-100)."""
        if self.ocr_result:
            return self.ocr_result.quality_score
        return None
    
    @property
    def is_high_quality(self) -> bool:
        """True si la calidad es superior al 80%."""
        quality = self.quality_score
        return quality is not None and quality >= 80.0
    
    @property
    def processing_summary(self) -> Dict[str, Any]:
        """Resumen de métricas del procesamiento."""
        summary = {
            'word_count': self.word_count,
            'table_count': self.table_count,
            'has_ocr_metrics': self.ocr_result is not None
        }
        
        if self.ocr_result:
            summary.update({
                'quality_score': self.quality_score,
                'processing_time': self.ocr_result.processing_time,
                'page_count': self.ocr_result.page_count,
                'is_high_quality': self.is_high_quality
            })
        
        return summary