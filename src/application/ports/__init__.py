# application/ports/__init__.py
"""
Puertos que definen las interfaces para los adaptadores externos.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Tuple

class OCRPort(ABC):
    """Puerto para servicios OCR."""
    
    @abstractmethod
    def extract_text(self, pdf_path: Path) -> str:
        """Extrae texto de un documento PDF."""
        pass

    @abstractmethod
    def get_confidence(self) -> float:
        """Retorna el nivel de confianza de la última extracción."""
        pass

class TableExtractorPort(ABC):
    """Puerto para extracción de tablas."""
    
    @abstractmethod
    def extract_tables(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extrae tablas de un documento PDF."""
        pass

class StoragePort(ABC):
    """Puerto para almacenamiento de resultados."""
    
    @abstractmethod
    def save_text(self, filename: str, content: str) -> Path:
        """Guarda contenido textual."""
        pass
    
    @abstractmethod
    def save_tables(self, filename: str, tables: List[Dict[str, Any]]) -> Path:
        """Guarda tablas extraídas."""
        pass
    
    @abstractmethod
    def save(self, doc_name: str, text: str, tables: List[Dict[str, Any]], pdf_path: Path) -> Tuple[Path, List[Path]]:
        """Guarda todos los resultados del procesamiento."""
        pass
