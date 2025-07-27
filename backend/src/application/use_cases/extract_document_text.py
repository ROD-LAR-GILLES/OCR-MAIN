"""
Caso de uso para extraer texto de documentos.
"""
from pathlib import Path
import logging

from domain.ports import OCRPort

logger = logging.getLogger(__name__)

class ExtractDocumentTextUseCase:
    """Caso de uso para extraer texto de documentos PDF."""

    def __init__(self, ocr: OCRPort) -> None:
        """Inicializa con dependencias inyectadas."""
        self.ocr = ocr

    def execute(self, pdf_path: Path) -> tuple[str, float]:
        """
        Extrae texto de un documento PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            tuple[str, float]: Texto extraído y nivel de confianza
        """
        logger.info(f"Extrayendo texto de: {pdf_path}")
        extracted_text = self.ocr.extract_text(pdf_path)
        confidence = self.ocr.get_confidence()
        
        logger.info(f"Texto extraído: {len(extracted_text)} caracteres")
        logger.info(f"Confianza OCR: {confidence:.1f}%")
        
        return extracted_text, confidence