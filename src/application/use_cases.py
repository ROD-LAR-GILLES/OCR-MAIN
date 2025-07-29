"""
Casos de uso para procesamiento de documentos PDF.
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
            
            # 4. Crear documento resultado - ORDEN CORRECTO SIN KEYWORDS
            document = Document(
                output_dir.name,      # name: str
                pdf_path,             # path: Path
                extracted_text,       # extracted_text: str
                tables,              # tables: List[Dict[str, Any]]
                confidence,          # confidence: float
                output_dir,          # output_directory: Optional[Path]
                generated_files      # generated_files: Optional[List[Path]]
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


class EnhancedProcessDocument:
    """Caso de uso avanzado con métricas de calidad y numeración automática."""

    def __init__(
        self,
        ocr: OCRPort,
        table_extractor: TableExtractorPort,
        storage: StoragePort,
        min_quality_threshold: float = 60.0,
        enable_auto_retry: bool = True
    ) -> None:
        """Inicializa el caso de uso avanzado."""
        self.ocr = ocr
        self.table_extractor = table_extractor
        self.storage = storage
        self.min_quality_threshold = min_quality_threshold
        self.enable_auto_retry = enable_auto_retry

    def execute(self, pdf_path: Path) -> Tuple[Document, Dict[str, Any]]:
        """
        Ejecuta procesamiento con análisis de métricas y numeración automática.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Tuple con documento procesado y métricas
        """
        logger.info(f"Iniciando procesamiento mejorado de: {pdf_path}")
        start_time = time.time()
        
        # Métricas iniciales
        metrics = {
            'processing_summary': {
                'start_time': start_time,
                'filename': pdf_path.name,
                'file_size_mb': pdf_path.stat().st_size / (1024 * 1024)
            },
            'ocr_metrics': {},
            'table_metrics': {},
            'quality_analysis': {},
            'output_quality': {}
        }

        try:
            # Extracción de texto con análisis de calidad
            text = self.ocr.extract_text(pdf_path)
            confidence = self.ocr.get_confidence()
            
            metrics['ocr_metrics'] = {
                'processing_time': time.time() - start_time,
                'average_confidence': confidence
            }

            # Extracción de tablas
            table_start_time = time.time()
            tables = self.table_extractor.extract_tables(pdf_path)
            table_processing_time = time.time() - table_start_time
            
            metrics['table_metrics'] = {
                'processing_time': table_processing_time,
                'tables_found': len(tables) if tables else 0
            }

            # Almacenamiento con numeración automática
            doc_name = pdf_path.stem
            storage_start_time = time.time()
            
            output_dir, generated_files = self.storage.save(
                doc_name, text, tables, pdf_path
            )
            
            storage_time = time.time() - storage_start_time

            # Crear documento con nombre único - ORDEN CORRECTO SIN KEYWORDS
            document = Document(
                output_dir.name,    # name: str
                pdf_path,          # path: Path
                text,              # extracted_text: str
                tables,            # tables: List[Dict[str, Any]]
                confidence,        # confidence: float
                output_dir,        # output_directory: Optional[Path]
                generated_files    # generated_files: Optional[List[Path]]
            )

            # Métricas finales
            total_time = time.time() - start_time
            metrics['processing_summary'].update({
                'total_time_seconds': total_time,
                'storage_time': storage_time,
                'files_generated': len(generated_files),
                'unique_name_assigned': document.name != doc_name
            })
            
            metrics['quality_analysis'] = {
                'ocr_quality': confidence,
                'meets_threshold': confidence >= self.min_quality_threshold
            }
            
            metrics['output_quality'] = {
                'word_count': len(text.split()) if text else 0,
                'table_count': len(tables) if tables else 0,
                'high_quality_result': confidence >= 80
            }
            
            logger.info(f"Procesamiento mejorado completado en {total_time:.2f}s")
            logger.info(f"Documento único: {document.name}")
            
            return document, metrics

        except Exception as e:
            error_time = time.time() - start_time
            metrics['processing_summary'].update({
                'total_time_seconds': error_time,
                'error': str(e),
                'success': False
            })
            
            logger.error(f"Error en procesamiento mejorado: {e}")
            raise ProcessingError(f"Error en procesamiento mejorado: {e}")

    def __call__(self, pdf_path: Path) -> Tuple[Document, Dict[str, Any]]:
        """Permite usar la clase como función."""
        return self.execute(pdf_path)
