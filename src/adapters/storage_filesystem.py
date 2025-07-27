# adapters/storage_filesystem.py
"""
Adaptador de almacenamiento basado en sistema de archivos local.

Este módulo implementa el puerto StoragePort para persistir los resultados
del procesamiento OCR en el sistema de archivos local, generando múltiples
formatos de salida para diferentes casos de uso.
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
    Adaptador de almacenamiento que persiste resultados en el sistema de archivos.
    
    NUEVA FUNCIONALIDAD: Crea una carpeta dedicada por cada documento procesado
    para mejor organización y evitar conflictos de archivos.
    
    Esta implementación genera múltiples formatos de salida organizados por documento:
    
    Estructura de directorios:
    resultado/
    ├── documento1/
    │   ├── texto_completo.txt           <- Texto plano extraído por OCR
    │   ├── documento1.md                <- Documento Markdown con texto y tablas
    │   └── documento1_original.pdf      <- Copia del archivo original
    └── documento2/
        ├── texto_completo.txt
        ├── documento2.md
        └── documento2_original.pdf
    
    Ventajas de la organización por carpetas:
    - Evita conflictos de nombres entre documentos
    - Facilita el backup y archivado por documento
    - Permite procesamiento de múltiples archivos con el mismo nombre
    - Estructura más clara para herramientas de automatización
    - Mejor integración con sistemas de versionado
    
    Formatos generados por documento:
    1. texto_completo.txt - Texto plano extraído por OCR (legible por humanos)
    2. [nombre].md - Documento Markdown estructurado con texto y tablas (documentación)
    3. [nombre]_original.pdf - Copia del archivo original (trazabilidad)
    
    Ventajas del almacenamiento en archivos:
    - Simple y rápido de implementar
    - No requiere infraestructura adicional (BD, cloud)
    - Fácil integración con herramientas de línea de comandos
    - Formatos estándar legibles por múltiples aplicaciones
    - Backup y versionado simple con herramientas estándar
    
    Limitaciones:
    - No soporta consultas complejas
    - Sin control de concurrencia
    - Escalabilidad limitada para grandes volúmenes
    - Sin índices para búsqueda rápida
    """

    def __init__(self, out_dir: Path) -> None:
        """
        Inicializa el adaptador de almacenamiento con directorio de salida.
        
        Args:
            out_dir (Path): Directorio donde se guardarán los archivos procesados.
                           Se crea automáticamente si no existe.
                           
        Note:
            - parents=True crea directorios padre si no existen
            - exist_ok=True evita errores si el directorio ya existe
        """
        self.out_dir = out_dir
        # Crea la estructura de directorios de forma segura
        # parents=True equivale a 'mkdir -p' en Unix
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, text: str, tables: List[Any], original: Path) -> List[str]:
        """
        Persiste los resultados del procesamiento en múltiples formatos dentro de una carpeta específica.
        
        NUEVA LÓGICA: Crea una carpeta por documento procesado y organiza todos
        los archivos resultantes dentro de esa carpeta para mejor organización.
        
        Genera una suite completa de archivos de salida para diferentes casos de uso:
        - Análisis manual (TXT legible)
        - Documentación estructurada (Markdown formateado) 
        - Trazabilidad (PDF original)
        
        Args:
            name (str): Nombre base para los archivos generados (sin extensión)
            text (str): Texto completo extraído por OCR
            tables (List[Any]): Lista de DataFrames con las tablas detectadas
            original (Path): Ruta al archivo PDF original
            
        Returns:
            List[str]: Lista de rutas de todos los archivos generados
            
        Estructura de archivos generados:
            resultado/
            └── documento/
                ├── texto_completo.txt          <- Texto completo OCR
                ├── documento.md                <- Documento Markdown estructurado
                └── documento_original.pdf      <- Copia del PDF original
            
        Raises:
            OSError: Si hay problemas de permisos o espacio en disco
        """
        # Crear carpeta específica para este documento
        document_folder = self.out_dir / name
        document_folder.mkdir(parents=True, exist_ok=True)
        
        archivos_generados = []

        # 1. TEXTO PLANO - Para lectura humana y análisis manual
        # Guarda el texto completo extraído por OCR en formato UTF-8
        # Útil para: búsquedas de texto, análisis de contenido, revisión manual
        texto_path = document_folder / "texto_completo.txt"
        texto_path.write_text(text, encoding="utf-8")
        archivos_generados.append(str(texto_path))

        # 2. ARCHIVO MARKDOWN - Para documentación estructurada
        # Genera un archivo Markdown que replica la estructura original del documento
        # Las tablas se integran en su posición original dentro del texto
        markdown_content = f"# Documento Procesado: {name}\n\n"
        
        if tables:
            # Integrar tablas en su posición original dentro del texto
            integrated_text = self._integrate_tables_in_text_simple(text, tables)
            markdown_content += integrated_text
        else:
            markdown_content += text
        
        markdown_path = document_folder / f"{name}.md"
        markdown_path.write_text(markdown_content, encoding="utf-8")
        archivos_generados.append(str(markdown_path))

        # 3. COPIA DEL PDF ORIGINAL - Para trazabilidad y referencia
        # Mantiene el archivo original junto con los resultados procesados
        # Útil para: auditoría, comparación, reprocesamiento si es necesario
        pdf_copy_path = document_folder / f"{name}_original.pdf"
        shutil.copy(original, pdf_copy_path)
        archivos_generados.append(str(pdf_copy_path))
        
        return archivos_generados
    
    def save_document(self, document) -> Tuple[str, List[str]]:
        """
        Guarda un documento completo con todas sus métricas y metadatos.
        
        Args:
            document: Instancia de Document con OCRResult y métricas
            
        Returns:
            Tuple[str, List[str]]: Directorio de salida y lista de archivos generados
        """
        # Usar el método save existente
        archivos_generados = self.save(
            document.name,
            document.extracted_text,
            document.tables,
            document.source_path
        )
        
        # Generar archivo de métricas adicional si está disponible
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
                # Si falla, continuar sin el archivo de métricas
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
            
        # Estrategia simplificada: agregar todas las tablas al final del texto
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