"""
Puerto para servicios OCR - Domain Layer.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List


class OCRPort(ABC):
    """
    Puerto que define las operaciones de OCR para procesamiento de documentos.
    
    Este puerto debe ser implementado por adaptadores que proporcionen
    servicios de OCR específicos como Tesseract, Google Vision, etc.
    """
    
    @abstractmethod
    def extract_text(self, pdf_path: Path, **options) -> str:
        """
        Extrae texto de un archivo PDF utilizando OCR.
        
        Args:
            pdf_path: Ruta al archivo PDF
            **options: Opciones específicas de extracción
            
        Returns:
            str: Texto extraído del documento
        """
        ...
    
    @abstractmethod
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el motor OCR.
        
        Returns:
            Dict[str, Any]: Información del motor
        """
        ...
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        Obtiene la lista de idiomas soportados.
        
        Returns:
            List[str]: Lista de códigos de idioma soportados
        """
        ...