"""
Factory para crear adaptadores - Clean Architecture.
"""
from pathlib import Path
import logging

from application.ports import OCRPort, TableExtractorPort, StoragePort
from infrastructure.config.system_config import SystemConfig
from domain.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV
from domain.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class AdapterFactory:
    """Factory para crear adaptadores siguiendo clean architecture."""
    
    @staticmethod
    def create_ocr_adapter(config: SystemConfig) -> OCRPort:
        """Crea adaptador OCR según configuración."""
        logger.info(f"Creando adaptador OCR: {config.engine_type}")
        
        from adapters.ocr.tesseract_adapter import TesseractAdapter
        from adapters.ocr.tesseract_opencv_adapter import TesseractOpenCVAdapter
        
        if config.engine_type == ENGINE_TYPE_BASIC:
            return TesseractAdapter.from_config(config)
        elif config.engine_type == ENGINE_TYPE_OPENCV:
            return TesseractOpenCVAdapter.from_config(config)
        else:
            raise ConfigurationError(f"Motor OCR no soportado: {config.engine_type}")
    
    @staticmethod
    def create_table_extractor() -> TableExtractorPort:
        """Crea extractor de tablas."""
        logger.info("Creando extractor de tablas")
        
        from adapters.table_simple import SimpleTableAdapter
        return SimpleTableAdapter()
    
    @staticmethod
    def create_storage_adapter(output_dir: Path) -> StoragePort:
        """Crea adaptador de almacenamiento."""
        logger.info(f"Creando adaptador de almacenamiento: {output_dir}")
        
        from adapters.storage.file_storage import FileStorage
        return FileStorage(output_dir)