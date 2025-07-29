"""
Implementación de almacenamiento en sistema de archivos.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

from application.ports import StoragePort
from domain.exceptions import StorageError


class FileStorage(StoragePort):
    """Adaptador para almacenamiento en sistema de archivos."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_text(self, filename: str, content: str) -> Path:
        """Guarda contenido textual."""
        try:
            output_path = self.output_dir / filename
            output_path.write_text(content, encoding='utf-8')
            return output_path
            
        except Exception as e:
            raise StorageError(f"Error guardando texto: {str(e)}")
    
    def save_tables(self, filename: str, tables: List[Dict[str, Any]]) -> Path:
        """Guarda tablas extraídas."""
        try:
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tables, f, indent=2, ensure_ascii=False)
            return output_path
            
        except Exception as e:
            raise StorageError(f"Error guardando tablas: {str(e)}")
    
    def save(self, doc_name: str, text: str, tables: List[Dict[str, Any]], pdf_path: Path) -> Tuple[Path, List[Path]]:
        """
        Guarda todos los resultados del procesamiento.
        
        Args:
            doc_name: Nombre del documento
            text: Texto extraído
            tables: Tablas extraídas
            pdf_path: Ruta original del PDF
            
        Returns:
            Tuple con archivo principal y lista de archivos generados
        """
        generated_files = []
        
        # Guardar texto
        text_file = self.save_text(f"{doc_name}_text.txt", text)
        generated_files.append(text_file)
        
        # Guardar tablas si existen
        if tables:
            tables_file = self.save_tables(f"{doc_name}_tables.json", tables)
            generated_files.append(tables_file)
        
        return text_file, generated_files