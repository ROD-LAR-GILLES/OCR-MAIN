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
            doc_name = pdf_path.stem  
            logger.info(f"Guardando resultados para: {doc_name}")
            
            output_dir, generated_files = self.storage.save(
                doc_name, extracted_text, tables, pdf_path
            )
            
            # DEBUG: Ver qué campos acepta realmente el modelo Document
            logger.info(f"DEBUG - Campos del modelo Document: {Document.__dataclass_fields__.keys()}")
            
            # 4. Crear documento resultado - DETECTAR MODELO AUTOMÁTICAMENTE
            try:
                # Intentar con todos los campos
                document = Document(
                    name=output_dir.name,
                    path=pdf_path,
                    extracted_text=extracted_text,
                    tables=tables,
                    confidence=confidence,
                    output_directory=output_dir,
                    generated_files=generated_files
                )
                logger.info("SUCCESS: Modelo Document completo usado")
            except TypeError as e:
                logger.warning(f"Modelo completo falló: {e}")
                try:
                    # Intentar sin path
                    document = Document(
                        name=output_dir.name,
                        extracted_text=extracted_text,
                        tables=tables,
                        confidence=confidence,
                        output_directory=output_dir,
                        generated_files=generated_files
                    )
                    logger.info("SUCCESS: Modelo Document sin 'path' usado")
                except TypeError as e2:
                    logger.warning(f"Modelo sin path falló: {e2}")
                    # Intentar modelo básico
                    document = Document(
                        name=output_dir.name,
                        extracted_text=extracted_text,
                        tables=tables,
                        confidence=confidence
                    )
                    logger.info("SUCCESS: Modelo Document básico usado")
                    # Agregar campos manualmente si existen
                    if hasattr(document, 'output_directory'):
                        document.output_directory = output_dir
                    if hasattr(document, 'generated_files'):
                        document.generated_files = generated_files
            
            processing_time = time.time() - start_time
            logger.info(f"Procesamiento completado en {processing_time:.2f}s")
            logger.info(f"Documento único: {document.name}")
            
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