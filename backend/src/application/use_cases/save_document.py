"""
Caso de uso para guardar documentos procesados.
"""
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging

from domain.ports import StoragePort
from domain.entities.document import Document

logger = logging.getLogger(__name__)

class SaveDocumentUseCase:
    """Caso de uso para guardar documentos procesados con numeración automática."""

    def __init__(self, storage: StoragePort) -> None:
        """Inicializa con dependencias inyectadas."""
        self.storage = storage

    def execute(
        self, 
        doc_name: str, 
        extracted_text: str, 
        tables: List[Dict[str, Any]], 
        pdf_path: Path
    ) -> Tuple[Path, List[Path]]:
        """
        Guarda un documento procesado con numeración automática.
        
        Args:
            doc_name: Nombre base del documento
            extracted_text: Texto extraído
            tables: Tablas extraídas
            pdf_path: Ruta original al PDF
            
        Returns:
            Tuple[Path, List[Path]]: Directorio de salida y archivos generados
        """
        logger.info(f"Guardando resultados para: {doc_name}")
        
        # Crear un objeto Document para pasar a save_document
        document = Document(
            name=doc_name,
            text=extracted_text,
            tables=tables,
            source_path=str(pdf_path)
        )
        
        # Usar save_document en lugar de save
        generated_files = self.storage.save_document(document)
        
        # Determinar el directorio de salida (el parent del primer archivo generado)
        output_dir = generated_files[0].parent if generated_files else None
        
        # Mostrar si se usó numeración
        if output_dir and output_dir.name != doc_name:
            logger.info(f"Numeración aplicada: '{doc_name}' → '{output_dir.name}'")
            
        logger.info(f"Archivos generados: {len(generated_files)}")
        
        return output_dir, generated_files