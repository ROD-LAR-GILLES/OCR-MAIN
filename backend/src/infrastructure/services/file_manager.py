import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from interfaces.api.models.uploaded_file import UploadedFile

class PersistentFileManager:
    """Gestor de archivos persistente usando sistema de archivos."""
    
    def __init__(self, storage_dir: str = "pdfs", metadata_file: str = "files_metadata.json"):
        self.storage_dir = Path(storage_dir)
        self.metadata_file = Path(metadata_file)
        self.storage_dir.mkdir(exist_ok=True)
        
    def save_file_metadata(self, uploaded_file: UploadedFile) -> None:
        """Guardar metadatos de archivo en JSON."""
        metadata = self._load_metadata()
        metadata[uploaded_file.file_id] = uploaded_file.model_dump()
        self._save_metadata(metadata)
    
    def get_file_metadata(self, file_id: str) -> Optional[UploadedFile]:
        """Obtener metadatos de archivo."""
        metadata = self._load_metadata()
        if file_id in metadata:
            return UploadedFile(**metadata[file_id])
        return None
    
    def list_files(self) -> List[UploadedFile]:
        """Listar todos los archivos."""
        metadata = self._load_metadata()
        return [UploadedFile(**data) for data in metadata.values()]
    
    def delete_file(self, file_id: str) -> bool:
        """Eliminar archivo y metadatos."""
        metadata = self._load_metadata()
        if file_id not in metadata:
            return False
            
        # Eliminar archivo físico
        file_data = metadata[file_id]
        file_path = Path(file_data['file_path'])
        if file_path.exists():
            file_path.unlink()
        
        # Eliminar metadatos
        del metadata[file_id]
        self._save_metadata(metadata)
        return True
    
    def _load_metadata(self) -> Dict:
        """Cargar metadatos desde archivo JSON."""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_metadata(self, metadata: Dict) -> None:
        """Guardar metadatos en archivo JSON."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)