"""
Factory de servicios de aplicación.
"""
from pathlib import Path

from application.ports import OCRPort, TableExtractorPort, StoragePort
from infrastructure.config import SystemConfig
from domain.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV
from domain.exceptions import ConfigurationError


class AdapterFactory:
    """Factory para crear adaptadores desde la capa de aplicación."""
    
    @staticmethod
    def create_ocr_adapter(config: SystemConfig) -> OCRPort:
        """Crea adaptador OCR según configuración."""
        from adapters.ocr import TesseractAdapter, TesseractOpenCVAdapter
        
        if config.engine_type == ENGINE_TYPE_BASIC:
            return TesseractAdapter.from_config(config)
        elif config.engine_type == ENGINE_TYPE_OPENCV:
            return TesseractOpenCVAdapter.from_config(config)
        else:
            raise ConfigurationError(f"Motor OCR no soportado: {config.engine_type}")
    
    @staticmethod
    def create_table_extractor() -> TableExtractorPort:
        """Crea extractor de tablas."""
        from adapters.table_pdfplumber import PdfPlumberAdapter
        return PdfPlumberAdapter()
    
    @staticmethod
    def create_storage_adapter(output_dir: Path) -> StoragePort:
        """Crea adaptador de almacenamiento."""
        from adapters.storage_filesystem import FileStorage
        return FileStorage(output_dir)