"""
Puerto para extracción de tablas - Domain Layer.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any


class TableExtractorPort(ABC):
    """
    Puerto que define las operaciones para extracción de tablas de documentos.
    
    Este puerto debe ser implementado por adaptadores que proporcionen
    servicios de extracción de tablas de documentos PDF.
    """
    
    @abstractmethod
    def extract_tables(self, pdf_path: Path, **options) -> List[Dict[str, Any]]:
        """
        Extrae tablas de un archivo PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            **options: Opciones específicas de extracción
            
        Returns:
            List[Dict[str, Any]]: Lista de tablas extraídas
        """
        ...
    
    @abstractmethod
    def get_extractor_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el extractor de tablas.
        
        Returns:
            Dict[str, Any]: Información del extractor
        """
        ...