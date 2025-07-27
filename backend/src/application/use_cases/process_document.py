"""
Caso de uso principal para procesamiento de documentos.
"""
from pathlib import Path
import logging
import time

from domain.ports import OCRPort, TableExtractorPort, StoragePort
from domain.models import Document
from domain.exceptions import ProcessingError
from application.use_cases.extract_document_text import ExtractDocumentTextUseCase
from application.use_cases.extract_tables import ExtractTablesUseCase
from application.use_cases.save_document import SaveDocumentUseCase

logger = logging.getLogger(__name__)

class ProcessDocument:
    """Caso de uso principal que orquesta el procesamiento completo de documentos."""

    def __init__(
        self,
        ocr: OCRPort,
        table_extractor: TableExtractorPort,
        storage: StoragePort,
    ) -> None:
        """Inicializa con dependencias inyectadas."""
        # Crear casos de uso específicos
        self.extract_text_use_case = ExtractDocumentTextUseCase(ocr)
        self.extract_tables_use_case = ExtractTablesUseCase(table_extractor)
        self.save_document_use_case = SaveDocumentUseCase(storage)

    def execute(self, pdf_path: Path) -> Document:
        """
        Ejecuta el procesamiento completo del documento.
        
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
            
            # 1. Extraer texto usando caso de uso específico
            extracted_text, confidence = self.extract_text_use_case.execute(pdf_path)
            
            # 2. Extraer tablas usando caso de uso específico
            tables = self.extract_tables_use_case.execute(pdf_path)
            
            # 3. Guardar resultados usando caso de uso específico
            doc_name = pdf_path.stem
            output_dir, generated_files = self.save_document_use_case.execute(
                doc_name, extracted_text, tables, pdf_path
            )
            
            # 4. Crear documento usando el modelo de dominio
            document = Document(
                name=output_dir.name,
                source_path=str(pdf_path),
                extracted_text=extracted_text,
                tables=tables or []
            )
            
            # Agregar campos adicionales
            document.confidence = confidence
            document.output_directory = output_dir
            document.generated_files = generated_files
            document.processing_time = time.time() - start_time
            
            # Registrar información
            processing_time = time.time() - start_time
            logger.info(f"Procesamiento completado en {processing_time:.2f}s")
            logger.info(f"Documento único: {document.name}")
            
            return document
            
        except Exception as e:
            logger.error(f"Error en procesamiento: {str(e)}")
            raise ProcessingError(f"Error procesando {pdf_path}: {str(e)}")

    def __call__(self, pdf_path: Path) -> Document:
        """Permite usar la clase como función."""
        return self.execute(pdf_path)