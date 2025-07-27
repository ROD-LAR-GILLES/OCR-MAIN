"""
Servicio para procesamiento de documentos.
"""
from pathlib import Path
from typing import List, Dict, Any
import logging

from application.ports import OCRPort, TableExtractorPort, StoragePort
from domain.models import Document
from domain.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Servicio para procesamiento de documentos."""

    def __init__(
        self,
        ocr: OCRPort,
        table_extractor: TableExtractorPort,
        storage: StoragePort,
    ) -> None:
        """Inicializa el procesador con adaptadores."""
        self.ocr = ocr
        self.table_extractor = table_extractor
        self.storage = storage

    def process(self, pdf_path: Path) -> Document:
        """
        Procesa un documento PDF completo.
        """
        try:
            logger.info(f"Iniciando procesamiento de documento: {pdf_path}")
            
            # Extraer texto
            text = self.ocr.extract_text(pdf_path)
            confidence = self.ocr.get_confidence()
            
            # Extraer tablas
            tables = self.table_extractor.extract_tables(pdf_path)
            
            # Guardar resultados con numeración automática
            doc_name = pdf_path.stem
            output_dir, generated_files = self.storage.save(
                doc_name, text, tables, pdf_path
            )
            
            # Crear documento usando el modelo CORRECTO
            document = Document(
                name=output_dir.name,           # Nombre único
                source_path=str(pdf_path),      # ← 'source_path', NO 'path'
                extracted_text=text,
                tables=tables or []
            )
            
            # Agregar campos adicionales
            document.confidence = confidence
            document.output_directory = output_dir
            document.generated_files = generated_files
            
            logger.info(f"Documento procesado exitosamente: {document.name}")
            return document
            
        except Exception as e:
            logger.error(f"Error en procesamiento de documento: {str(e)}")
            raise ProcessingError(f"Error procesando documento: {str(e)}")