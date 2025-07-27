"""
Entidad Document - Dominio
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime


class Document:
    """
    Entidad que representa un documento procesado.
    
    Esta es una entidad del dominio que encapsula toda la información
    relacionada con un documento procesado por el sistema OCR.
    """
    
    def __init__(
        self,
        name: str,
        text: str = "",
        tables: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None,
        id: str = None,
        source_path: str = None,  # Añadido este parámetro
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        """
        Inicializa un documento.
        
        Args:
            name: Nombre del documento
            text: Texto extraído del documento
            tables: Tablas extraídas (opcional)
            metadata: Metadatos del documento (opcional)
            id: Identificador único (se genera si no se proporciona)
            source_path: Ruta al archivo fuente original (opcional)
            created_at: Fecha de creación (se usa now() si no se proporciona)
            updated_at: Fecha de actualización (igual a created_at si no se proporciona)
        """
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.text = text
        self.tables = tables or []
        self.metadata = metadata or {}
        self.source_path = source_path  # Guardamos la ruta fuente
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        
        # Atributos adicionales que pueden ser asignados más tarde
        self.confidence = None
        self.output_directory = None
        self.generated_files = None
        self.processing_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el documento a un diccionario.
        
        Returns:
            Dict[str, Any]: Representación como diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "text_length": len(self.text),
            "tables_count": len(self.tables),
            "metadata": self.metadata,
            "source_path": self.source_path,
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @property
    def is_empty(self) -> bool:
        """
        Verifica si el documento está vacío.
        
        Returns:
            bool: True si el documento no tiene texto ni tablas
        """
        return not self.text and not self.tables