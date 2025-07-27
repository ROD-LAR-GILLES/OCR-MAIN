"""
Configuración del sistema OCR - Capa de Infraestructura.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from domain.constants import (
    DEFAULT_LANGUAGE,
    DEFAULT_DPI,
    DEFAULT_CONFIDENCE_THRESHOLD,
    ENGINE_TYPE_BASIC,
    HIGH_QUALITY_THRESHOLD,
    MEDIUM_QUALITY_THRESHOLD
)

# Perfiles de calidad predefinidos
QUALITY_PROFILES = {
    "fast": {
        "dpi": 150,
        "confidence_threshold": 50.0,
        "engine_type": ENGINE_TYPE_BASIC
    },
    "balanced": {
        "dpi": 300,
        "confidence_threshold": 60.0,
        "engine_type": ENGINE_TYPE_BASIC
    },
    "high": {
        "dpi": 600,
        "confidence_threshold": 80.0,
        "engine_type": ENGINE_TYPE_BASIC
    }
}


@dataclass
class SystemConfig:
    """Configuración del sistema OCR."""
    
    # Configuración OCR
    language: str = DEFAULT_LANGUAGE
    dpi: int = DEFAULT_DPI
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    engine_type: str = ENGINE_TYPE_BASIC
    
    # Directorios
    output_dir: Path = Path("resultado")
    temp_dir: Path = Path("temp")
    
    # Configuración de calidad
    quality_profile: str = "balanced"
    
    def __post_init__(self):
        """Inicialización post-creación."""
        # Convertir strings a Path si es necesario
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.temp_dir, str):
            self.temp_dir = Path(self.temp_dir)
            
        # Crear directorios si no existen
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_quality_profile(cls, profile_name: str) -> 'SystemConfig':
        """Crea configuración basada en perfil de calidad."""
        if profile_name not in QUALITY_PROFILES:
            raise ValueError(f"Perfil no válido: {profile_name}")
        
        profile = QUALITY_PROFILES[profile_name]
        return cls(
            dpi=profile["dpi"],
            confidence_threshold=profile["confidence_threshold"],
            engine_type=profile["engine_type"],
            quality_profile=profile_name
        )