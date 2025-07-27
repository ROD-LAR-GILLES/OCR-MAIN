# config/system_config.py
"""
Configuraciones del sistema OCR-CLI.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from shared.constants import (
    DEFAULT_LANGUAGE, DEFAULT_DPI, DEFAULT_CONFIDENCE_THRESHOLD,
    ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV
)


@dataclass
class SystemConfig:
    """Configuración unificada del sistema OCR-CLI."""
    # OCR Settings
    language: str = DEFAULT_LANGUAGE
    dpi: int = DEFAULT_DPI
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    engine_type: str = ENGINE_TYPE_BASIC  # "basic" o "opencv"
    
    # OpenCV Preprocessing
    enable_deskewing: bool = True
    enable_denoising: bool = True
    enable_contrast_enhancement: bool = True
    
    # Processing Settings
    enable_auto_retry: bool = True
    max_processing_time_minutes: int = 30
    enable_table_extraction: bool = True
    
    @classmethod
    def create_high_quality_config(cls) -> 'SystemConfig':
        """Configuración para máxima calidad."""
        return cls(
            dpi=600,
            confidence_threshold=80.0,
            engine_type=ENGINE_TYPE_OPENCV,
            enable_deskewing=True,
            enable_denoising=True,
            enable_contrast_enhancement=True,
            enable_auto_retry=True,
            max_processing_time_minutes=60
        )
    
    @classmethod
    def create_fast_config(cls) -> 'SystemConfig':
        """Configuración para procesamiento rápido."""
        return cls(
            dpi=150,
            confidence_threshold=50.0,
            engine_type=ENGINE_TYPE_BASIC,
            enable_deskewing=False,
            enable_denoising=False,
            enable_contrast_enhancement=True,
            enable_auto_retry=False,
            max_processing_time_minutes=10
        )
    
    @classmethod
    def create_balanced_config(cls) -> 'SystemConfig':
        """Configuración balanceada (por defecto)."""
        return cls()


# Perfiles de calidad simplificados
QUALITY_PROFILES = {
    'maximum_quality': SystemConfig.create_high_quality_config(),
    'fast_processing': SystemConfig.create_fast_config(),
    'balanced': SystemConfig.create_balanced_config()
}
