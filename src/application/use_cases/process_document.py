"""
Caso de uso para procesamiento de documentos.
"""
from pathlib import Path
from typing import Tuple, Dict, Any
import logging

from application.ports import OCRPort, TableExtractorPort, StoragePort
from domain.models import Document
from domain.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class ProcessDocument:
    """Caso de uso para procesar documentos PDF."""
    
    def __init__(
        self,
        ocr_service: OCRPort,
        table_extractor: TableExtractorPort,
        storage: StoragePort
    ):
        self.ocr = ocr_service
        self.table_extractor = table_extractor
        self.storage = storage

    def execute(self, pdf_path: Path) -> Document:
        """
        Ejecuta el procesamiento completo del documento.
        
        Args:
            pdf_path: Ruta al archivo PDF a procesar
            
        Returns:
            Document: Documento procesado con resultados
            
        Raises:
            ProcessingError: Si hay error en el procesamiento
        """
        try:
            logger.info(f"Iniciando procesamiento de: {pdf_path}")
            
            # Validar que el archivo existe
            if not pdf_path.exists():
                raise ProcessingError(f"Archivo no encontrado: {pdf_path}")
            
            # Extraer texto usando OCR
            logger.info("Extrayendo texto...")
            text = self.ocr.extract_text(pdf_path)
            
            # Extraer tablas
            logger.info("Extrayendo tablas...")
            tables = self.table_extractor.extract_tables(pdf_path)
            
            # Crear documento con resultados
            document = Document(
                name=pdf_path.stem,
                source_path=str(pdf_path),
                extracted_text=text,
                tables=tables
            )
            
            # Guardar resultados
            logger.info("Guardando resultados...")
            main_file, generated_files = self.storage.save(
                document.name,
                document.extracted_text,
                document.tables,
                pdf_path
            )
            
            logger.info(f"Procesamiento completado. Archivos generados: {len(generated_files)}")
            return document
            
        except Exception as e:
            logger.error(f"Error procesando documento: {str(e)}")
            raise ProcessingError(f"Error procesando {pdf_path}: {str(e)}")