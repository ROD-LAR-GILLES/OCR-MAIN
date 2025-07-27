"""
Configuración de dependencias para la API.
"""
import logging
from functools import lru_cache

# SOLO importar desde infrastructure (ubicación correcta)
from infrastructure.config.system_config import SystemConfig, QUALITY_PROFILES

logger = logging.getLogger(__name__)

@lru_cache()
def get_system_config() -> SystemConfig:
    """
    Obtener configuración del sistema como singleton.
    
    Returns:
        SystemConfig: Configuración del sistema usando perfil balanced
    """
    try:
        # Usar el método from_quality_profile que ya existe
        config = SystemConfig.from_quality_profile("balanced")
        
        # Agregar propiedades de compatibilidad para la API
        config.output_directory = str(config.output_dir)
        config.input_directory = "pdfs"
        config.extract_tables = True
        config.temp_directory = str(config.temp_dir)
        
        logger.info(f" Configuración cargada: perfil {config.quality_profile}")
        logger.info(f" DPI: {config.dpi}, Confianza: {config.confidence_threshold}")
        logger.info(f" Output: {config.output_dir}")
        
        return config
        
    except Exception as e:
        logger.error(f" Error cargando configuración: {e}")
        
        # Fallback: configuración por defecto
        config = SystemConfig()
        config.output_directory = str(config.output_dir)
        config.input_directory = "pdfs"
        config.extract_tables = True
        config.temp_directory = str(config.temp_dir)
        
        logger.warning(" Usando configuración de fallback")
        return config