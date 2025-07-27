"""
Lógica de menús y validación de opciones.

"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from config.system_config import SystemConfig


@dataclass
class MenuOption:
    """
    Opción de menú con ID, texto y valor.
    
    """
    id: int
    text: str
    value: str = ""


def create_pdf_menu_options(pdf_files: List[str]) -> List[MenuOption]:
    """
    Crea opciones de menú para archivos PDF.
    
    """
    options = []
    for i, filename in enumerate(pdf_files, 1):
        options.append(MenuOption(id=i, text=f"{i}. {filename}", value=filename))
    
    # Agregar opción de salida
    exit_id = len(pdf_files) + 1
    options.append(MenuOption(id=exit_id, text=f"{exit_id}. Salir", value="exit"))
    
    return options


def validate_menu_selection(selection: int, total_options: int) -> bool:
    """
    Valida si la selección está dentro del rango de opciones.
    
    """
    return 1 <= selection <= total_options


def get_selected_pdf(pdf_files: List[str], selection: int) -> str:
    """
    Devuelve el nombre del PDF seleccionado según la opción elegida.

    """
    if not pdf_files:
        raise ValueError("No hay archivos PDF disponibles")
    
    if not validate_menu_selection(selection, len(pdf_files)):
        raise ValueError(f"Selección {selection} fuera de rango. Opciones válidas: 1-{len(pdf_files)}")
    
    try:
        return pdf_files[selection - 1]  # Convertir a 0-indexed
    except IndexError as e:
        raise IndexError(f"Error de índice al seleccionar archivo: {e}")


def is_exit_selection(selection: int, total_pdf_files: int) -> bool:
    """
    Devuelve True si la selección es la opción de salida.
    
    """
    return selection == total_pdf_files + 1


def create_ocr_config_from_user_choices(
    engine_choice: int,
    enable_deskewing: bool = True,
    enable_denoising: bool = True,
    enable_contrast: bool = True
) -> SystemConfig:
    """
    Crea una configuración OCR según la opción y ajustes elegidos.

    """
    if engine_choice == 1:
        return SystemConfig(
            language="spa",
            dpi=300,
            engine_type="basic",
            enable_deskewing=False,
            enable_denoising=False,
            enable_contrast_enhancement=False
        )
    elif engine_choice == 2:
        return SystemConfig(
            language="spa",
            dpi=300,
            engine_type="opencv",
            enable_deskewing=enable_deskewing,
            enable_denoising=enable_denoising,
            enable_contrast_enhancement=enable_contrast
        )
    else:
        raise ValueError(f"Opción de motor inválida: {engine_choice}. Use 1 (básico) o 2 (OpenCV)")


def detect_pdf_type_automatically(pdf_path: Path) -> Tuple[SystemConfig, str]:
    """
    Detecta automáticamente el tipo de PDF y retorna la configuración óptima.
    
    Returns:
        Tuple[SystemConfig, str]: (configuración_óptima, descripción_detección)
    """
    try:
        # Análisis básico usando Path y heurísticas simples
        filename = pdf_path.name.lower()
        
        # Heurísticas basadas en nombre de archivo
        if any(word in filename for word in ['scan', 'escaneado', 'escan']):
            config = SystemConfig(
                language="spa",
                dpi=300,
                engine_type="opencv",
                enable_deskewing=True,
                enable_denoising=True,
                enable_contrast_enhancement=True
            )
            return config, "Documento escaneado - OCR intensivo con preprocesamiento"
        
        if any(word in filename for word in ['digital', 'nativo', 'text']):
            config = SystemConfig(
                language="spa",
                dpi=150,
                engine_type="basic",
                enable_deskewing=False,
                enable_denoising=False,
                enable_contrast_enhancement=False
            )
            return config, "PDF nativo - Extracción directa de texto"
        
        if any(word in filename for word in ['tabla', 'table', 'form', 'formulario']):
            config = SystemConfig(
                language="spa",
                dpi=300,
                engine_type="opencv",
                enable_deskewing=False,
                enable_denoising=True,
                enable_contrast_enhancement=True
            )
            return config, "Documento con tablas - Extracción estructurada"
        
        # Por defecto: configuración balanceada para documento mixto
        config = SystemConfig(
            language="spa",
            dpi=250,
            engine_type="opencv",
            enable_deskewing=True,
            enable_denoising=False,
            enable_contrast_enhancement=True
        )
        return config, "Documento mixto - Configuración balanceada"
        
    except Exception:
        # Fallback seguro con configuración conservadora
        config = SystemConfig(
            language="spa",
            dpi=300,
            engine_type="opencv",
            enable_deskewing=True,
            enable_denoising=False,
            enable_contrast_enhancement=True
        )
        return config, "Configuración automática (modo seguro)"


def validate_ocr_engine_choice(choice: int) -> bool:
    """
    Valida que la elección del motor OCR sea válida.

    """
    return choice in [1, 2, 3]
