"""
Servicio de aplicación para procesamiento de documentos.
"""
from pathlib import Path
from typing import Tuple, List, Dict, Any
import logging

from application.ports import OCRPort, TableExtractorPort, StoragePort
from domain.models import Document, OCRResult
from domain.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class DocumentProcessorService:
    """Servicio de aplicación para procesamiento de documentos."""
    
    def __init__(
        self,
        ocr: OCRPort,
        table_extractor: TableExtractorPort,
        storage: StoragePort
    ):
        self.ocr = ocr
        self.table_extractor = table_extractor
        self.storage = storage
    
    def process_document(self, pdf_path: Path) -> Document:
        """
        Procesa un documento PDF completo.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Document: Documento procesado con resultados
        """
        try:
            logger.info(f"Iniciando procesamiento de: {pdf_path}")
            
            # Extraer texto
            text = self.ocr.extract_text(pdf_path)
            
            # Extraer tablas
            tables = self.table_extractor.extract_tables(pdf_path)
            
            # Crear documento
            document = Document(
                name=pdf_path.stem,
                source_path=str(pdf_path),
                extracted_text=text,
                tables=tables
            )
            
            # Guardar resultados
            main_file, generated_files = self.storage.save(
                document.name,
                document.extracted_text,
                document.tables,
                pdf_path
            )
            
            logger.info(f"Documento procesado exitosamente: {len(generated_files)} archivos generados")
            return document
            
        except Exception as e:
            raise ProcessingError(f"Error procesando documento {pdf_path}: {str(e)}")