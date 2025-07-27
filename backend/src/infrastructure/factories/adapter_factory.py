"""
Factory para crear adaptadores.
"""
from pathlib import Path
import logging

# Imports del dominio
from domain.ports.ocr_port import OCRPort
from domain.ports.table_extractor_port import TableExtractorPort
from domain.ports.storage_port import StoragePort
from infrastructure.config.system_config import SystemConfig
from domain.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV
from domain.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


# ✅ ESTRUCTURA IDEAL SEGÚN CLEAN ARCHITECTURE
class AdapterFactory:
    """Factory para crear adaptadores siguiendo clean architecture."""
    
    @staticmethod
    def create_ocr_adapter(config: SystemConfig) -> OCRPort:
        """Crea adaptador OCR según configuración."""
        logger.info(f"Creando adaptador OCR: {config.engine_type}")

        from infrastructure.adapters.ocr.tesseract_adapter import TesseractAdapter
        from infrastructure.adapters.ocr.tesseract_opencv_adapter import TesseractOpenCVAdapter
        
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
        
        from infrastructure.adapters.table_simple import SimpleTableAdapter
        return SimpleTableAdapter()
    
    @staticmethod  
    def create_storage_adapter(output_dir: Path) -> StoragePort:
        """Crea adaptador de almacenamiento."""
        logger.info(f"Creando adaptador de almacenamiento: {output_dir}")
        
        from infrastructure.adapters.storage.file_storage import FileStorage
        return FileStorage(output_dir)
