"""
Adaptador para almacenamiento en sistema de archivos.
"""
import logging
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from domain.ports import StoragePort
from domain.entities.document import Document

logger = logging.getLogger(__name__)

class FileStorage(StoragePort):
    """Implementación de StoragePort usando sistema de archivos."""
    
    def __init__(self, output_dir: Path):
        """Inicializa el adaptador con directorio de salida."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"FileStorage inicializado: {output_dir}")
    
    def save_document(self, document: "Document") -> List[Path]:
        """
        Guarda un documento procesado.
        
        Args:
            document: Documento procesado
            
        Returns:
            List[Path]: Lista de rutas a los archivos generados
        """
        # Supongamos que document tiene los siguientes atributos:
        # - name: nombre del documento
        # - text: texto extraído
        # - tables: tablas extraídas
        # - source_path: ruta al PDF original
        
        # Crear directorio único para el documento
        doc_dir = self._create_unique_dir(document.name)
        
        generated_files = []
        
        # Guardar texto extraído
        text_file = doc_dir / f"{doc_dir.name}_texto.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(document.text)
        generated_files.append(text_file)
        
        # Guardar tablas como JSON si hay
        if document.tables:
            tables_file = doc_dir / f"{doc_dir.name}_tablas.json"
            with open(tables_file, "w", encoding="utf-8") as f:
                json.dump(document.tables, f, ensure_ascii=False, indent=2)
            generated_files.append(tables_file)
        
        # Copiar PDF original si existe
        if hasattr(document, 'source_path') and document.source_path:
            pdf_path = Path(document.source_path)
            if pdf_path.exists():
                pdf_copy = doc_dir / f"{doc_dir.name}_original.pdf"
                shutil.copy2(pdf_path, pdf_copy)
                generated_files.append(pdf_copy)
        
        # Guardar metadatos
        metadata = {
            "id": document.id if hasattr(document, 'id') else None,
            "name": document.name,
            "text_length": len(document.text),
            "tables_count": len(document.tables),
            "confidence": document.confidence if hasattr(document, 'confidence') else None,
            "processing_time": document.processing_time if hasattr(document, 'processing_time') else None,
        }
        
        metadata_file = doc_dir / f"{doc_dir.name}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        generated_files.append(metadata_file)
        
        return generated_files
    
    def get_document(self, document_id: str) -> Optional["Document"]:
        """
        Obtiene un documento almacenado.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Optional[Document]: Documento recuperado o None si no existe
        """
        # En una implementación simple, document_id podría ser el nombre de la carpeta
        doc_dir = self.output_dir / document_id
        
        if not doc_dir.exists() or not doc_dir.is_dir():
            return None
        
        # Buscar archivo de metadatos
        metadata_files = list(doc_dir.glob(f"{document_id}_metadata.json"))
        if not metadata_files:
            return None
        
        # Cargar metadatos
        with open(metadata_files[0], "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Buscar archivo de texto
        text_files = list(doc_dir.glob(f"{document_id}_texto.txt"))
        text = ""
        if text_files:
            with open(text_files[0], "r", encoding="utf-8") as f:
                text = f.read()
        
        # Buscar archivo de tablas
        tables = []
        tables_files = list(doc_dir.glob(f"{document_id}_tablas.json"))
        if tables_files:
            with open(tables_files[0], "r", encoding="utf-8") as f:
                tables = json.load(f)
        
        # Crear documento
        document = Document(
            name=document_id,
            text=text,
            tables=tables,
        )
        
        # Agregar campos adicionales si existen en metadatos
        if "id" in metadata:
            document.id = metadata["id"]
        if "confidence" in metadata:
            document.confidence = metadata["confidence"]
        if "processing_time" in metadata:
            document.processing_time = metadata["processing_time"]
        
        return document
    
    def list_documents(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista documentos almacenados.
        
        Args:
            limit: Límite de documentos a retornar
            offset: Desplazamiento para paginación
            
        Returns:
            List[Dict[str, Any]]: Lista de metadatos de documentos
        """
        # Listar directorios en el directorio de salida
        doc_dirs = [d for d in self.output_dir.iterdir() if d.is_dir()]
        doc_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Aplicar paginación
        paginated_dirs = doc_dirs[offset:offset+limit]
        
        # Recopilar metadatos
        results = []
        for doc_dir in paginated_dirs:
            # Buscar archivo de metadatos
            metadata_files = list(doc_dir.glob(f"{doc_dir.name}_metadata.json"))
            if not metadata_files:
                # Si no hay metadatos, crear básicos
                results.append({
                    "id": doc_dir.name,
                    "name": doc_dir.name,
                    "created_at": doc_dir.stat().st_mtime
                })
                continue
            
            # Cargar metadatos
            with open(metadata_files[0], "r", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata["id"] = doc_dir.name
                results.append(metadata)
        
        return results
    
    def _create_unique_dir(self, base_name: str) -> Path:
        """Crea un directorio único basado en el nombre base."""
        unique_dir = self.output_dir / base_name
        counter = 1
        
        while unique_dir.exists():
            unique_name = f"{base_name}_{counter:02d}"
            unique_dir = self.output_dir / unique_name
            counter += 1
        
        unique_dir.mkdir(parents=True, exist_ok=True)
        return unique_dir  # Asegúrate de tener este return
    
    def save(self, doc_name: str, extracted_text: str, tables: List[Dict[str, Any]], pdf_path: Path) -> Tuple[Path, List[Path]]:
        """
        Método de compatibilidad para casos de uso existentes.
        
        Args:
            doc_name: Nombre del documento
            extracted_text: Texto extraído
            tables: Tablas extraídas
            pdf_path: Ruta al PDF original
            
        Returns:
            Tuple[Path, List[Path]]: Directorio de salida y archivos generados
        """
        # Crear un objeto Document temporal
        document = Document(
            name=doc_name,
            text=extracted_text,
            tables=tables,
            source_path=str(pdf_path)
        )
        
        # Llamar a save_document
        generated_files = self.save_document(document)
        
        # Determinar el directorio de salida
        output_dir = generated_files[0].parent if generated_files else None
        
        return output_dir, generated_files