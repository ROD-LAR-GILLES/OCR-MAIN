# application/ports/ocr_port.py
"""
Puerto para servicios de OCR.
"""
from abc import ABC, abstractmethod
from pathlib import Path


class OCRPort(ABC):
    """Puerto para servicios de OCR."""
    
    @abstractmethod
    def extract_text(self, pdf_path: Path) -> str:
        """
        Extrae texto de un PDF usando OCR.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Texto extraído del documento
        """
        ...
