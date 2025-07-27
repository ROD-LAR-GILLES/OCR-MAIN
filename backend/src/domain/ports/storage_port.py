"""
Puerto para almacenamiento de documentos - Domain Layer.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

# Importación condicional para evitar error circular
if TYPE_CHECKING:
    from domain.entities.document import Document


class StoragePort(ABC):
    """
    Puerto que define las operaciones para almacenar documentos procesados.
    
    Este puerto debe ser implementado por adaptadores que proporcionen
    servicios de almacenamiento como sistemas de archivos, bases de datos, etc.
    """
    
    @abstractmethod
    def save_document(self, document: "Document") -> List[Path]:
        """
        Guarda un documento procesado.
        
        Args:
            document: Documento procesado
            
        Returns:
            List[Path]: Lista de rutas a los archivos generados
        """
        ...
    
    @abstractmethod
    def get_document(self, document_id: str) -> Optional["Document"]:
        """
        Obtiene un documento almacenado.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Optional[Document]: Documento recuperado o None si no existe
        """
        ...
    
    @abstractmethod
    def list_documents(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista documentos almacenados.
        
        Args:
            limit: Límite de documentos a retornar
            offset: Desplazamiento para paginación
            
        Returns:
            List[Dict[str, Any]]: Lista de metadatos de documentos
        """
        ...