"""
Caso de uso para extraer tablas de documentos.
"""
from pathlib import Path
from typing import List, Dict, Any
import logging

from domain.ports import TableExtractorPort

logger = logging.getLogger(__name__)

class ExtractTablesUseCase:
    """Caso de uso para extraer tablas de documentos PDF."""

    def __init__(self, table_extractor: TableExtractorPort) -> None:
        """Inicializa con dependencias inyectadas."""
        self.table_extractor = table_extractor

    def execute(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extrae tablas de un documento PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            List[Dict[str, Any]]: Lista de tablas extraídas
        """
        logger.info(f"Extrayendo tablas de: {pdf_path}")
        tables = self.table_extractor.extract_tables(pdf_path)
        
        logger.info(f"Tablas encontradas: {len(tables)}")
        
        return tables