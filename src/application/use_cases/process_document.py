"""
Caso de uso para procesamiento de documentos.
"""
from pathlib import Path
from typing import Tuple, List, Any, Dict
import logging
import time

from application.ports import OCRPort, TableExtractorPort, StoragePort
from domain.models import Document
from domain.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class ProcessDocument:
    """Caso de uso para procesar documentos PDF con numeración automática."""

    def __init__(
        self,
        ocr: OCRPort,
        table_extractor: TableExtractorPort,
        storage: StoragePort,
    ) -> None:
        """Inicializa con dependencias inyectadas."""
        self.ocr = ocr
        self.table_extractor = table_extractor
        self.storage = storage

    def execute(self, pdf_path: Path) -> Document:
        """
        Ejecuta el procesamiento completo del documento con numeración automática.
        
        Args:
            pdf_path: Ruta al archivo PDF a procesar
            
        Returns:
            Document: Documento procesado con nombre único
            
        Raises:
            ProcessingError: Si hay error en el procesamiento
        """
        try:
            logger.info(f"Iniciando procesamiento de: {pdf_path}")
            start_time = time.time()
            
            # 1. Extraer texto usando OCR
            logger.info("Extrayendo texto...")
            extracted_text = self.ocr.extract_text(pdf_path)
            confidence = self.ocr.get_confidence()
            
            # 2. Extraer tablas
            logger.info("Extrayendo tablas...")
            tables = self.table_extractor.extract_tables(pdf_path)
            
            # 3. Guardar resultados con numeración automática
            doc_name = pdf_path.stem  # Nombre sin extensión
            logger.info(f"Guardando resultados para: {doc_name}")
            
            output_dir, generated_files = self.storage.save(
                doc_name, extracted_text, tables, pdf_path
            )
            
            # 4. Crear documento resultado - USAR KEYWORDS PARA CLARIDAD
            document = Document(
                name=output_dir.name,
                path=pdf_path,
                extracted_text=extracted_text,
                tables=tables,
                confidence=confidence,
                output_directory=output_dir,
                generated_files=generated_files
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Procesamiento completado en {processing_time:.2f}s")
            logger.info(f"Documento único: {document.name}")
            logger.info(f"Archivos generados: {len(generated_files)}")
            
            # Mostrar si se usó numeración
            if document.name != doc_name:
                logger.info(f"NUMERACION APLICADA: '{doc_name}' → '{document.name}'")
            
            return document
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {str(e)}")
            raise ProcessingError(f"Error procesando {pdf_path}: {str(e)}")

    def __call__(self, pdf_path: Path) -> Document:
        """Permite usar la clase como función."""
        return self.execute(pdf_path)