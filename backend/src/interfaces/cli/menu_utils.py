"""
Utilidades para menús CLI - Capa de Interfaces.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

# Actualizar imports para nueva arquitectura
from infrastructure.config.system_config import SystemConfig
from domain.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


@dataclass
class MenuOption:
    """Opción de menú con ID, texto y valor."""
    id: int
    text: str
    value: str = ""


def create_pdf_menu_options(pdf_files: List[str]) -> List[MenuOption]:
    """Crea opciones de menú para archivos PDF."""
    options = []
    for i, filename in enumerate(pdf_files, 1):
        option = MenuOption(
            id=i,
            text=f"{i:2d}. {filename}",
            value=filename
        )
        options.append(option)
    
    # Agregar opción de salida
    exit_id = len(pdf_files) + 1
    options.append(MenuOption(id=exit_id, text=f"{exit_id}. Salir", value="exit"))
    
    return options


def validate_menu_selection(choice: int, max_options: int) -> bool:
    """Valida que la selección del usuario esté en el rango válido."""
    return 1 <= choice <= max_options


def get_selected_pdf(pdf_files: List[str], choice: int) -> str:
    """Obtiene el archivo PDF seleccionado según la opción elegida."""
    if not validate_menu_selection(choice, len(pdf_files)):
        raise ValueError(f"Selección inválida: {choice}")
    
    return pdf_files[choice - 1]


def is_exit_selection(choice: int, total_files: int) -> bool:
    """Verifica si la selección corresponde a salir del menú."""
    return choice == total_files + 1


def validate_ocr_engine_choice(choice: int) -> bool:
    """Valida la selección del motor OCR."""
    return choice in [1, 2, 3]


def create_ocr_config_from_user_choices(engine_choice: int) -> SystemConfig:
    """Crea configuración OCR basada en la selección del usuario."""
    config = SystemConfig()
    
    if engine_choice == 1:
        # Motor básico
        config.engine_type = ENGINE_TYPE_BASIC
        config.dpi = 300
        config.confidence_threshold = 60.0
    elif engine_choice == 2:
        # Motor OpenCV
        config.engine_type = ENGINE_TYPE_OPENCV
        config.dpi = 400
        config.confidence_threshold = 70.0
        config.enable_deskewing = True
        config.enable_denoising = True
        config.enable_contrast_enhancement = True
    else:
        raise ValueError(f"Opción de motor inválida: {engine_choice}")
    
    config.language = DEFAULT_LANGUAGE
    logger.info(f"Configuración creada: {config.engine_type}")
    return config


def detect_pdf_type_automatically(file_path):
    """
    Detecta automáticamente el tipo de PDF.
    
    Args:
        file_path (str): Ruta al archivo PDF
        
    Returns:
        str: Tipo de PDF ('native', 'scanned', 'mixed', 'unknown')
    """
    try:
        from pathlib import Path
        
        # Asegurar que file_path es un Path object
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Verificar que el archivo existe
        if not file_path.exists():
            logger.warning(f"Archivo no encontrado: {file_path}")
            return "unknown"
        
        # Verificar tamaño del archivo
        file_size = file_path.stat().st_size
        if file_size == 0:
            logger.warning(f"Archivo vacío: {file_path}")
            return "unknown"
        
        # Lógica de detección de tipo
        # (aquí va tu lógica existente de detección)
        
        # Por ahora, retornar un tipo básico basado en el tamaño
        if file_size > 5_000_000:  # 5MB
            return "scanned"
        else:
            return "native"
            
    except Exception as e:
        logger.error(f"Error en detección automática: {e}")
        return "unknown"
