"""
Controladores de aplicación.
"""

import time
from pathlib import Path
from typing import Tuple, List, Dict, Any
import logging

from application.ports import OCRPort, TableExtractorPort, StoragePort
from application.use_cases import ProcessDocument
from config.system_config import SystemConfig
from domain.exceptions import DocumentNotFoundError, ProcessingError, ConfigurationError
from domain.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV
from infrastructure.factories import AdapterFactory

logger = logging.getLogger(__name__)


class DocumentController:
    """
    Controlador para procesar documentos PDF con diferentes configuraciones OCR.
    """
    
    def __init__(self, pdf_dir: Path, output_dir: Path):
        """
        Inicializa el controlador con directorios de trabajo.
        
        Args:
            pdf_dir (Path): Directorio donde se encuentran los PDFs
            output_dir (Path): Directorio donde guardar resultados
        """
        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
    
    def process_document(
        self, 
        filename: str, 
        ocr_config: SystemConfig
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Procesa un PDF usando la configuración OCR especificada.
        
        Args:
            filename: Nombre del archivo PDF
            ocr_config: Configuración OCR a usar
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (éxito, información_procesamiento)
        """
        pdf_path = self.pdf_dir / filename
        
        # Validar que el archivo existe
        if not pdf_path.exists():
            error_info = {
                "error": f"Archivo {filename} no encontrado",
                "filename": filename,
                "processing_time": 0
            }
            logger.error(f"Archivo no encontrado: {pdf_path}")
            return False, error_info
        
        try:
            logger.info(f"Iniciando procesamiento de {filename}")
            
            # Crear adaptadores usando factory
            ocr_adapter = AdapterFactory.create_ocr_adapter(ocr_config)
            table_adapter = AdapterFactory.create_table_extractor()
            storage_adapter = AdapterFactory.create_storage_adapter(self.output_dir)

            
            # Crear caso de uso
            processor = ProcessDocument(
                ocr=ocr_adapter,
                table_extractor=table_adapter,
                storage=storage_adapter
            )
            
            # Medir tiempo de procesamiento
            start_time = time.time()
            
            # Ejecutar procesamiento
            try:
                result = processor(pdf_path)
                
                # Verificar si es una tupla con 2 elementos
                if isinstance(result, tuple) and len(result) == 2:
                    texto_principal, archivos_generados = result
                else:
                    raise ProcessingError(f"ProcessDocument retornó {type(result)} en lugar de tupla de 2 elementos: {result}")
                    
            except Exception as debug_error:
                raise ProcessingError(f"Error en processor(): {debug_error}")
            
            processing_time = time.time() - start_time
            
            success_info = {
                "filename": filename,
                "processing_time": processing_time,
                "main_text_file": texto_principal,
                "generated_files": archivos_generados,
                "files_count": len(archivos_generados),
                "ocr_config": ocr_config,
                "error": None
            }
            
            logger.info(f"Procesamiento exitoso de {filename} en {processing_time:.2f}s")
            return True, success_info
            
        except (ConfigurationError, ProcessingError) as e:
            processing_time = time.time() - start_time if 'start_time' in locals() else 0
            error_info = {
                "filename": filename,
                "processing_time": processing_time,
                "error": str(e),
                "error_type": type(e).__name__,
                "ocr_config": ocr_config
            }
            logger.error(f"Error controlado procesando {filename}: {e}")
            return False, error_info
            
        except Exception as e:
            processing_time = time.time() - start_time if 'start_time' in locals() else 0
            error_info = {
                "filename": filename,
                "processing_time": processing_time,
                "error": str(e),
                "error_type": type(e).__name__,
                "ocr_config": ocr_config
            }
            logger.exception(f"Error inesperado procesando {filename}")
            return False, error_info
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """
        Retorna información sobre las capacidades de procesamiento disponibles.
        
        Returns:
            Dict: Información sobre motores OCR disponibles y configuraciones
        """
        return {
            "ocr_engines": {
                ENGINE_TYPE_BASIC: {
                    "name": "Tesseract básico",
                    "description": "OCR rápido para documentos de alta calidad",
                    "performance": "Alto",
                    "quality": "Bueno"
                },
                ENGINE_TYPE_OPENCV: {
                    "name": "Tesseract + OpenCV",
                    "description": "OCR avanzado con preprocesamiento",
                    "performance": "Medio",
                    "quality": "Excelente",
                    "features": [
                        "Corrección de inclinación",
                        "Eliminación de ruido",
                        "Mejora de contraste",
                        "Binarización adaptativa"
                    ]
                }
            },
            "supported_formats": ["PDF"],
            "output_formats": ["TXT", "JSON", "ASCII"],
            "directories": {
                "input": str(self.pdf_dir),
                "output": str(self.output_dir)
            }
        }
