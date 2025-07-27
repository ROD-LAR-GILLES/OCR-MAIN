"""
Controladores de aplicación para orquestar casos de uso.

Los controladores son el punto de entrada a la capa de aplicación.
Coordinan uno o más casos de uso para implementar las operaciones
del sistema, pero no contienen lógica de negocio.
"""
import logging
import time
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from domain.exceptions import OCRError, ProcessingError, ConfigurationError
from domain.entities.document import Document
from application.use_cases.process_document import ProcessDocument
from application.use_cases.extract_document_text import ExtractDocumentTextUseCase
from application.use_cases.extract_tables import ExtractTablesUseCase
from application.use_cases.save_document import SaveDocumentUseCase
from config.system_config import SystemConfig
from infrastructure.factories import AdapterFactory

logger = logging.getLogger(__name__)

class DocumentController:
    """
    Controlador para operaciones con documentos.
    
    Coordina casos de uso para implementar las operaciones
    relacionadas con el procesamiento de documentos.
    """
    
    def __init__(
        self,
        process_document_use_case: ProcessDocument,
        extract_text_use_case: Optional[ExtractDocumentTextUseCase] = None,
        extract_tables_use_case: Optional[ExtractTablesUseCase] = None,
        save_document_use_case: Optional[SaveDocumentUseCase] = None
    ):
        """
        Inicializa el controlador con los casos de uso necesarios.
        
        Args:
            process_document_use_case: Caso de uso principal
            extract_text_use_case: Caso de uso para extraer texto (opcional)
            extract_tables_use_case: Caso de uso para extraer tablas (opcional)
            save_document_use_case: Caso de uso para guardar documentos (opcional)
        """
        self.process_document = process_document_use_case
        self.extract_text = extract_text_use_case
        self.extract_tables = extract_tables_use_case
        self.save_document = save_document_use_case
    
    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Procesa un archivo PDF completo.
        
        Coordina el caso de uso ProcessDocument para realizar
        el procesamiento completo del documento.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento
        """
        try:
            logger.info(f"Procesando documento: {pdf_path}")
            
            # Delegar al caso de uso principal
            document = self.process_document(pdf_path)
            
            # Transformar resultado a formato de respuesta
            result = {
                "success": True,
                "document": document.name,
                "text_length": len(document.text),
                "tables_count": len(document.tables),
                "output_dir": str(document.output_directory),
                "confidence": document.confidence,
                "processing_time": document.processing_time,
                "message": "Proceso completado exitosamente!"
            }
            
            logger.info(f"Procesamiento completado: {document.name}")
            return result
            
        except (OCRError, ProcessingError) as e:
            logger.error(f"Error de dominio: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Error inesperado: {str(e)}"
            }
    
    def extract_document_text(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extrae solo texto de un documento PDF.
        
        Coordina el caso de uso ExtractDocumentTextUseCase.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict[str, Any]: Texto extraído y metadatos
        """
        if not self.extract_text:
            return {
                "success": False,
                "message": "Funcionalidad no disponible: extracción de texto"
            }
            
        try:
            logger.info(f"Extrayendo texto de: {pdf_path}")
            
            # Delegar al caso de uso específico
            text, confidence = self.extract_text.execute(pdf_path)
            
            return {
                "success": True,
                "text": text,
                "text_length": len(text),
                "confidence": confidence,
                "message": "Texto extraído correctamente"
            }
            
        except Exception as e:
            logger.error(f"Error en extracción de texto: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error en extracción de texto: {str(e)}"
            }
    
    def extract_document_tables(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extrae solo tablas de un documento PDF.
        
        Coordina el caso de uso ExtractTablesUseCase.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict[str, Any]: Tablas extraídas y metadatos
        """
        if not self.extract_tables:
            return {
                "success": False,
                "message": "Funcionalidad no disponible: extracción de tablas"
            }
            
        try:
            logger.info(f"Extrayendo tablas de: {pdf_path}")
            
            # Delegar al caso de uso específico
            tables = self.extract_tables.execute(pdf_path)
            
            return {
                "success": True,
                "tables": tables,
                "tables_count": len(tables),
                "message": "Tablas extraídas correctamente"
            }
            
        except Exception as e:
            logger.error(f"Error en extracción de tablas: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error en extracción de tablas: {str(e)}"
            }
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """
        Retorna información sobre las capacidades de procesamiento disponibles.
        
        Returns:
            Dict: Información sobre motores OCR disponibles y configuraciones
        """
        return {
            "ocr_engines": {
                "basic": {
                    "name": "Tesseract básico",
                    "description": "OCR rápido para documentos de alta calidad",
                    "performance": "Alto",
                    "quality": "Bueno"
                },
                "opencv": {
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
