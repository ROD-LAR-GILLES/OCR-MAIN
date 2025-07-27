"""
Servicio para generar archivos Markdown desde resultados OCR.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MarkdownGenerator:
    """Generador de archivos Markdown desde resultados OCR."""
    
    def __init__(self):
        self.template_header = """# {filename}

## Información del Documento

- **Archivo Original**: {filename}
- **Páginas Procesadas**: {total_pages}
- **Confianza OCR**: {confidence_score:.2%}
- **Tiempo de Procesamiento**: {processing_time:.2f} segundos
- **Fecha de Procesamiento**: {processed_date}
- **ID de Documento**: {document_id}

---

## Contenido Extraído

"""
    
    def generate_markdown(
        self,
        extracted_text: str,
        document_metadata: Dict[str, Any],
        tables: Optional[List[Dict]] = None,
        output_path: Path = None
    ) -> str:
        """
        Generar archivo Markdown desde resultados OCR.
        
        Args:
            extracted_text: Texto extraído del documento
            document_metadata: Metadatos del documento
            tables: Tablas extraídas (opcional)
            output_path: Ruta donde guardar el archivo
            
        Returns:
            str: Contenido Markdown generado
        """
        # Preparar metadatos
        metadata = {
            'filename': document_metadata.get('filename', 'documento.pdf'),
            'total_pages': document_metadata.get('total_pages', 0),
            'confidence_score': document_metadata.get('confidence_score', 0.0),
            'processing_time': document_metadata.get('processing_time', 0.0),
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'document_id': document_metadata.get('document_id', 'unknown')
        }
        
        # Generar header
        markdown_content = self.template_header.format(**metadata)
        
        # Agregar texto principal
        markdown_content += self._format_text_content(extracted_text)
        
        # Agregar tablas si existen
        if tables:
            markdown_content += self._format_tables(tables)
        
        # Agregar footer
        markdown_content += self._generate_footer(document_metadata)
        
        # Guardar archivo si se especifica ruta
        if output_path:
            self._save_markdown_file(markdown_content, output_path)
        
        return markdown_content
    
    def _format_text_content(self, text: str) -> str:
        """Formatear el contenido de texto."""
        if not text or not text.strip():
            return "*(No se extrajo texto del documento)*\n\n"
        
        # Limpiar y formatear texto
        formatted_text = text.strip()
        
        # Agregar saltos de línea para párrafos
        paragraphs = formatted_text.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Detectar posibles títulos (líneas cortas en mayúsculas)
                if (len(paragraph) < 100 and 
                    paragraph.isupper() and 
                    not paragraph.startswith(' ')):
                    formatted_paragraphs.append(f"### {paragraph}")
                else:
                    formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs) + '\n\n'
    
    def _format_tables(self, tables: List[Dict]) -> str:
        """Formatear tablas en formato Markdown."""
        if not tables:
            return ""
        
        tables_content = "## Tablas Extraídas\n\n"
        
        for i, table in enumerate(tables, 1):
            tables_content += f"### Tabla {i}\n\n"
            
            # Obtener datos de la tabla
            data = table.get('data', [])
            if not data:
                tables_content += "*(Tabla vacía)*\n\n"
                continue
            
            # Crear tabla Markdown
            if len(data) > 0:
                # Header
                headers = data[0] if data else []
                if headers:
                    tables_content += "| " + " | ".join(str(cell) for cell in headers) + " |\n"
                    tables_content += "|" + "---|" * len(headers) + "\n"
                    
                    # Filas de datos
                    for row in data[1:]:
                        tables_content += "| " + " | ".join(str(cell) for cell in row) + " |\n"
                
                tables_content += "\n"
            
            # Metadatos de la tabla
            if table.get('confidence'):
                tables_content += f"*Confianza: {table['confidence']:.2%}*\n\n"
        
        return tables_content
    
    def _generate_footer(self, metadata: Dict[str, Any]) -> str:
        """Generar footer del documento."""
        footer = """---

## Información Técnica

- **Motor OCR**: Tesseract
- **Configuración**: {tesseract_config}
- **DPI**: {dpi}
- **Idioma**: {language}

*Documento generado automáticamente por OCR Processing System v2.0.0*
"""
        
        footer_data = {
            'tesseract_config': metadata.get('tesseract_config', '--oem 3 --psm 6'),
            'dpi': metadata.get('dpi', 300),
            'language': metadata.get('language', 'spa')
        }
        
        return footer.format(**footer_data)
    
    def _save_markdown_file(self, content: str, output_path: Path) -> None:
        """Guardar contenido en archivo Markdown."""
        try:
            # Asegurar que el directorio existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            raise Exception(f"Error guardando archivo Markdown: {e}")
    
    def generate_summary_markdown(
        self,
        documents: List[Dict[str, Any]],
        output_path: Path = None
    ) -> str:
        """
        Generar resumen Markdown de múltiples documentos.
        
        Args:
            documents: Lista de metadatos de documentos
            output_path: Ruta donde guardar el resumen
            
        Returns:
            str: Contenido del resumen en Markdown
        """
        summary = f"""# Resumen de Procesamiento OCR

**Fecha de Generación**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total de Documentos**: {len(documents)}

## Documentos Procesados

| Documento | Páginas | Confianza | Tiempo | Estado |
|-----------|---------|-----------|--------|--------|
"""
        
        for doc in documents:
            summary += f"| {doc.get('filename', 'N/A')} | {doc.get('total_pages', 0)} | {doc.get('confidence_score', 0):.2%} | {doc.get('processing_time', 0):.2f}s | {doc.get('status', 'unknown')} |\n"
        
        summary += f"""
## Estadísticas

- **Total de Páginas**: {sum(doc.get('total_pages', 0) for doc in documents)}
- **Confianza Promedio**: {sum(doc.get('confidence_score', 0) for doc in documents) / len(documents) if documents else 0:.2%}
- **Tiempo Total**: {sum(doc.get('processing_time', 0) for doc in documents):.2f} segundos

---

*Generado por OCR Processing System v2.0.0*
"""
        
        if output_path:
            self._save_markdown_file(summary, output_path)
        
        return summary