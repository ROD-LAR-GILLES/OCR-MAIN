# application/ports/table_extractor_port.py
"""
Puerto para extracción de tablas de PDFs.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any


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
