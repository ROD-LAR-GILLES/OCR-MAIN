# adapters/pdf_info_adapter.py
"""
Obtención de información de archivos PDF.
"""
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class PdfInfoAdapter:
    """
    Adaptador para extraer metadatos básicos de archivos PDF.
    
    """
    
    def get_page_count(self, pdf_path: Path) -> int:
        """
        Obtiene el número de páginas de un archivo PDF.
        
        Args:
            pdf_path (Path): Ruta al archivo PDF
            
        Returns:
            int: Número de páginas del PDF
            
        Raises:
            Exception: Si hay problemas leyendo el PDF
        """
        try:
            # Intentar con PyPDF2 primero
            return self._get_page_count_pypdf2(pdf_path)
        except Exception as e:
            logger.warning(f"Error con PyPDF2: {e}, intentando con pdfplumber")
            try:
                return self._get_page_count_pdfplumber(pdf_path)
            except Exception as e2:
                logger.warning(f"Error con pdfplumber: {e2}, usando fallback")
                return 1  # Fallback seguro
    
    def _get_page_count_pypdf2(self, pdf_path: Path) -> int:
        """Obtiene páginas usando PyPDF2."""
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    
    def _get_page_count_pdfplumber(self, pdf_path: Path) -> int:
        """Obtiene páginas usando pdfplumber."""
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    
    def get_file_metadata(self, pdf_path: Path) -> dict:
        """
        Obtiene metadatos básicos del archivo PDF.
        
        Args:
            pdf_path (Path): Ruta al archivo PDF
            
        Returns:
            dict: Metadatos del archivo
        """
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata or {}
                
                return {
                    'page_count': len(reader.pages),
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'creation_date': metadata.get('/CreationDate', ''),
                    'modification_date': metadata.get('/ModDate', '')
                }
        except Exception as e:
            logger.warning(f"Error obteniendo metadatos: {e}")
            return {
                'page_count': self.get_page_count(pdf_path),
                'title': '',
                'author': '',
                'creator': '',
                'producer': '',
                'creation_date': '',
                'modification_date': ''
            }
