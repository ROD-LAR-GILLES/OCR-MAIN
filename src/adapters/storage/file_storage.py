"""
Adaptador de almacenamiento en sistema de archivos.
"""
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime

from application.ports import StoragePort
from domain.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class FileStorage(StoragePort):
    """Adaptador para almacenamiento en sistema de archivos."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileStorage inicializado: {self.output_dir}")
    
    def _generate_unique_name(self, base_name: str) -> str:
        """
        Genera un nombre único agregando numeración si es necesario.
        
        Args:
            base_name: Nombre base del documento
            
        Returns:
            Nombre único con numeración si es necesario
        """
        # Verificar si existe el directorio base
        base_path = self.output_dir / base_name
        
        if not base_path.exists():
            # Si no existe, usar el nombre original
            logger.info(f"Usando nombre original: {base_name}")
            return base_name
        
        # Si existe, buscar el siguiente número disponible
        counter = 1
        while True:
            numbered_name = f"{base_name}_{counter:02d}"
            numbered_path = self.output_dir / numbered_name
            
            if not numbered_path.exists():
                logger.info(f"Nombre único generado: {numbered_name} (evitando duplicado)")
                return numbered_name
            
            counter += 1
            
            # Prevenir bucle infinito (máximo 99 versiones)
            if counter > 99:
                raise ProcessingError(f"Demasiadas versiones del documento {base_name}")

    def save_text(self, filename: str, content: str) -> Path:
        """Guarda contenido textual en archivo."""
        try:
            text_path = self.output_dir / f"{filename}_texto.txt"
            text_path.write_text(content, encoding="utf-8")
            
            logger.info(f"Texto guardado: {text_path}")
            return text_path
            
        except Exception as e:
            logger.error(f"Error guardando texto: {str(e)}")
            raise ProcessingError(f"Error guardando texto: {str(e)}")

    def save_tables(self, filename: str, tables: List[Dict[str, Any]]) -> Path:
        """Guarda tablas extraídas en archivo JSON."""
        try:
            tables_path = self.output_dir / f"{filename}_tablas.json"
            
            # Convertir tablas a formato serializable
            tables_data = {
                "total_tables": len(tables),
                "tables": tables
            }
            
            tables_path.write_text(
                json.dumps(tables_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            
            logger.info(f"Tablas guardadas: {tables_path}")
            return tables_path
            
        except Exception as e:
            logger.error(f"Error guardando tablas: {str(e)}")
            raise ProcessingError(f"Error guardando tablas: {str(e)}")

    def save(self, doc_name: str, text: str, tables: List[Dict[str, Any]], pdf_path: Path) -> Tuple[Path, List[Path]]:
        """
        Guarda todos los resultados del procesamiento con numeración automática.
        
        Args:
            doc_name: Nombre base del documento
            text: Texto extraído
            tables: Tablas extraídas
            pdf_path: Ruta al PDF original
            
        Returns:
            Tuple con directorio de salida y lista de archivos generados
        """
        try:
            # PASO CRÍTICO: Generar nombre único ANTES de crear cualquier archivo
            unique_name = self._generate_unique_name(doc_name)
            document_folder = self.output_dir / unique_name
            
            # Crear directorio con el nombre único
            document_folder.mkdir(parents=True, exist_ok=True)
            
            logger.info(f" Guardando resultados en: {document_folder}")
            logger.info(f"  Nombre único asignado: {unique_name}")
            
            archivos_generados = []
            
            # 1. Guardar texto extraído
            text_path = document_folder / f"{unique_name}_texto.txt"
            text_path.write_text(text, encoding="utf-8")
            archivos_generados.append(text_path)
            logger.info(f" Texto guardado: {text_path.name}")
            
            # 2. Guardar tablas (si existen)
            if tables:
                tables_path = document_folder / f"{unique_name}_tablas.json"
                tables_data = {
                    "documento": unique_name,
                    "total_tablas": len(tables),
                    "fecha_procesamiento": datetime.now().isoformat(),
                    "tablas": tables
                }
                tables_path.write_text(
                    json.dumps(tables_data, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                archivos_generados.append(tables_path)
                logger.info(f" Tablas guardadas: {tables_path.name}")
            
            # 3. Crear resumen en Markdown
            markdown_path = document_folder / f"{unique_name}_resumen.md"
            markdown_content = self._create_markdown_summary(unique_name, text, tables)
            markdown_path.write_text(markdown_content, encoding="utf-8")
            archivos_generados.append(markdown_path)
            logger.info(f" Resumen guardado: {markdown_path.name}")
            
            # 4. Copiar PDF original
            pdf_copy_path = document_folder / f"{unique_name}_original.pdf"
            shutil.copy(pdf_path, pdf_copy_path)
            archivos_generados.append(pdf_copy_path)
            logger.info(f" PDF copiado: {pdf_copy_path.name}")
            
            # 5. Crear archivo de metadatos
            metadata_path = document_folder / f"{unique_name}_metadata.json"
            metadata = {
                "nombre_original": doc_name,
                "nombre_unico": unique_name,
                "archivo_original": str(pdf_path),
                "caracteres_texto": len(text),
                "numero_tablas": len(tables),
                "fecha_procesamiento": datetime.now().isoformat(),
                "archivos_generados": [p.name for p in archivos_generados]
            }
            metadata_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            archivos_generados.append(metadata_path)
            logger.info(f" Metadatos guardados: {metadata_path.name}")
            
            logger.info(f" Procesamiento completado:")
            logger.info(f"    Archivos generados: {len(archivos_generados)}")
            logger.info(f"    Directorio: {document_folder.name}")
            
            # Mostrar comparación de nombres si es diferente
            if unique_name != doc_name:
                logger.info(f"    Nombre original: '{doc_name}' → Nombre único: '{unique_name}'")
            
            return document_folder, archivos_generados
            
        except Exception as e:
            logger.error(f" Error guardando resultados: {str(e)}")
            raise ProcessingError(f"Error guardando resultados: {str(e)}")
    
    def _create_markdown_summary(self, doc_name: str, text: str, tables: List[Dict[str, Any]]) -> str:
        """Crea un resumen en formato Markdown."""
        summary = f"""# Resumen de Procesamiento OCR

## Documento: {doc_name}

### Estadísticas
- **Caracteres extraídos:** {len(text):,}
- **Tablas encontradas:** {len(tables)}
- **Fecha de procesamiento:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Texto Extraído (Primeros 500 caracteres)
```
{text[:500]}{'...' if len(text) > 500 else ''}
```

"""
        
        if tables:
            summary += "### Tablas Detectadas\n\n"
            for i, table in enumerate(tables, 1):
                summary += f"**Tabla {i}:** Página {table.get('page', '?')}, "
                summary += f"{table.get('rows', 0)} filas, {table.get('columns', 0)} columnas\n\n"
        else:
            summary += "### Tablas\nNo se detectaron tablas en el documento.\n\n"
        
        return summary