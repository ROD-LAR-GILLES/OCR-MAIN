# shared/factories/adapter_factory.py
"""
Factory para crear adaptadores basado en configuración.
"""
from pathlib import Path
from typing import Protocol

from application.ports import OCRPort, TableExtractorPort, StoragePort
from config.system_config import SystemConfig
from shared.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV
from shared.exceptions import ConfigurationError


class AdapterFactory:
    """Factory para crear adaptadores sin violar la arquitectura."""
    
    @staticmethod
    def create_ocr_adapter(config: SystemConfig) -> OCRPort:
        """
        Crea el adaptador OCR apropiado basado en la configuración.
        
        Args:
            config: Configuración del sistema
            
        Returns:
            OCRPort: Adaptador OCR configurado
            
        Raises:
            ConfigurationError: Si el tipo de motor no es soportado
        """
        # Lazy import para evitar dependencias circulares
        from adapters.ocr_adapters import TesseractAdapter, TesseractOpenCVAdapter
        
        if config.engine_type == ENGINE_TYPE_BASIC:
            return TesseractAdapter.from_config(config)
        elif config.engine_type == ENGINE_TYPE_OPENCV:
            return TesseractOpenCVAdapter.from_config(config)
        else:
            raise ConfigurationError(f"Tipo de motor OCR no soportado: {config.engine_type}")
    
    @staticmethod
    def create_table_extractor() -> TableExtractorPort:
        """
        Crea el extractor de tablas.
        
        Returns:
            TableExtractorPort: Extractor de tablas configurado
        """
        # Lazy import para evitar dependencias circulares
        from adapters.table_pdfplumber import PdfPlumberAdapter
        
        return PdfPlumberAdapter()
    
    @staticmethod
    def create_storage_adapter(output_dir: Path) -> StoragePort:
        """
        Crea el adaptador de almacenamiento.
        
        Args:
            output_dir: Directorio de salida
            
        Returns:
            StoragePort: Adaptador de almacenamiento configurado
        """
        # Lazy import para evitar dependencias circulares
        from adapters.storage_filesystem import FileStorage
        
        return FileStorage(output_dir)
