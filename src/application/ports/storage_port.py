# application/ports/storage_port.py
"""
Puerto para persistencia de resultados.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Any


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
