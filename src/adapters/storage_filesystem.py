# adapters/storage_filesystem.py
"""
Almacenamiento en sistema de archivos con estructura por documento.
"""
import shutil
from pathlib import Path
from typing import List, Any, Tuple
import pandas as pd
from tabulate import tabulate
from datetime import datetime

from application.ports import StoragePort


class FileStorage(StoragePort):
    """
    Almacena resultados en carpetas por documento.
    
    Estructura: resultado/documento/[texto.txt, doc.md, original.pdf]
    """

    def __init__(self, out_dir: Path) -> None:
        """Inicializa el adaptador con directorio de salida."""
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, text: str, tables: List[Any], original: Path) -> List[str]:
        """
        Persiste los resultados en carpeta específica del documento.
        
        Args:
            name: Nombre base del documento
            text: Texto extraído por OCR
            tables: Lista de DataFrames con tablas
            original: Ruta al PDF original
            
        Returns:
            Lista de archivos generados
        """
        document_folder = self.out_dir / name
        document_folder.mkdir(parents=True, exist_ok=True)
        
        archivos_generados = []

        texto_path = document_folder / "texto_completo.txt"
        texto_path.write_text(text, encoding="utf-8")
        archivos_generados.append(str(texto_path))

        markdown_content = f"# Documento Procesado: {name}\n\n"
        
        if tables:
            integrated_text = self._integrate_tables_in_text_simple(text, tables)
            markdown_content += integrated_text
        else:
            markdown_content += text
        
        markdown_path = document_folder / f"{name}.md"
        markdown_path.write_text(markdown_content, encoding="utf-8")
        archivos_generados.append(str(markdown_path))

        pdf_copy_path = document_folder / f"{name}_original.pdf"
        shutil.copy(original, pdf_copy_path)
        archivos_generados.append(str(pdf_copy_path))
        
        return archivos_generados
    
    def save_document(self, document) -> Tuple[str, List[str]]:
        """
        Guarda un documento completo con todas sus métricas y metadatos.
        
        Args:    document: Instancia de Document con OCRResult y métricas
        Returns: Tuple[str, List[str]]: Directorio de salida y lista de archivos generados
        """
        archivos_generados = self.save(
            document.name,
            document.extracted_text,
            document.tables,
            document.source_path
        )
        
        if document.ocr_result:
            document_folder = self.out_dir / document.name
            metrics_path = document_folder / f"{document.name}_metrics.json"
            
            try:
                import json
                metrics_data = {
                    'processing_summary': document.processing_summary,
                    'ocr_metrics': {
                        'quality_score': document.ocr_result.quality_score,
                        'processing_time': document.ocr_result.processing_time,
                        'page_count': document.ocr_result.page_count,
                        'confidence': document.ocr_result.metrics.average_confidence
                    },
                    'document_metadata': document.processing_metadata
                }
                
                with open(metrics_path, 'w', encoding='utf-8') as f:
                    json.dump(metrics_data, f, indent=2, ensure_ascii=False)
                
                archivos_generados.append(str(metrics_path))
            except Exception as e:
                pass
        
        return str(self.out_dir / document.name), archivos_generados

    def _integrate_tables_in_text_simple(self, text: str, tables: List[Any]) -> str:
        """
        Integra las tablas en el texto de forma simple y efectiva.
        
        Args:
            text (str): Texto completo extraído
            tables (List[Any]): Lista de DataFrames con tablas
            
        Returns:
            str: Texto con tablas integradas en formato markdown
        """
        if not tables:
            return text
            
        result = text + "\n\n## Tablas Extraídas\n\n"
        
        for i, df in enumerate(tables, 1):
            result += f"### Tabla {i}\n\n"
            result += self._format_table_as_markdown(df)
            result += "\n\n"
            
        return result
    
    def _format_table_as_markdown(self, df: pd.DataFrame) -> str:
        """
        Convierte un DataFrame a formato markdown.
        
        Args:
            df: DataFrame a convertir
            
        Returns:
            str: Tabla en formato markdown
        """
        try:
            return tabulate(df, headers='keys', tablefmt='pipe', showindex=False)
        except Exception:
            return f"Error formateando tabla: {df.shape[0]} filas x {df.shape[1]} columnas"