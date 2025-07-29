"""
Adaptador simple para extracción de tablas.
"""
from pathlib import Path
import logging
from typing import List, Dict, Any

from application.ports import TableExtractorPort

logger = logging.getLogger(__name__)


class SimpleTableAdapter(TableExtractorPort):
    """Adaptador simple que no extrae tablas pero cumple la interfaz."""
    
    def __init__(self):
        logger.info("SimpleTableAdapter inicializado")
    
    def extract_tables(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Simulación de extracción de tablas - retorna lista vacía.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista vacía
        """
        logger.info(f"Omitiendo extracción de tablas de: {pdf_path}")
        return []