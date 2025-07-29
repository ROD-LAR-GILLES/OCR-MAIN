"""
Configuración del sistema - ARCHIVO DE COMPATIBILIDAD.
Este archivo mantiene la compatibilidad mientras migramos.
"""
# Importar desde la nueva ubicación
from infrastructure.config.system_config import SystemConfig as NewSystemConfig
from infrastructure.config.system_config import QUALITY_PROFILES

# Crear alias para mantener compatibilidad
SystemConfig = NewSystemConfig

# Re-exportar todo lo necesario
__all__ = ['SystemConfig', 'QUALITY_PROFILES']
