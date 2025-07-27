# application/ports.py
"""
Puertos (interfaces) para arquitectura hexagonal.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any


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


class TableExtractorPort(ABC):
    """Puerto para extracción de tablas de PDFs."""
    
    @abstractmethod
    def extract_tables(self, pdf_path: Path) -> List[Any]:
        """
        Extrae tablas de un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de DataFrames con las tablas encontradas
        """
        ...


class StoragePort(ABC):
    """Puerto para persistencia de resultados."""
    
    @abstractmethod
    def save(self, name: str, text: str, tables: List[Any], original: Path) -> List[str]:
        """
        Persiste los resultados del procesamiento.
        
        Args:
            name: Nombre identificador del documento
            text: Texto extraído por OCR
            tables: Lista de tablas extraídas
            original: Ruta al archivo PDF original
            
        Returns:
            Lista de rutas de archivos generados
        """
        ...