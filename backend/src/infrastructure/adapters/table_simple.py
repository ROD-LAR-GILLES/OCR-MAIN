"""
Adaptador simple para extracción de tablas.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any

from domain.ports.table_extractor_port import TableExtractorPort

logger = logging.getLogger(__name__)


class SimpleTableAdapter(TableExtractorPort):
    """Implementación simple de extractor de tablas."""
    
    def extract_tables(self, pdf_path: Path, **options) -> List[Dict[str, Any]]:
        """
        Extrae tablas de un archivo PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            **options: Opciones específicas de extracción
            
        Returns:
            List[Dict[str, Any]]: Lista de tablas extraídas
        """
        logger.info(f"Extrayendo tablas de {pdf_path}")
        # Implementación básica, devuelve lista vacía
        return []
    
    def get_extractor_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre el extractor de tablas.
        
        Returns:
            Dict[str, Any]: Información del extractor
        """
        return {
            "name": "Simple Table Extractor",
            "version": "1.0.0",
            "capabilities": ["basic_table_detection"],
        }