"""
Interfaz de línea de comandos.
"""
from .menu import main as cli_main
from .interactive_menu import main as interactive_main, InteractiveMenu
from .menu_utils import (
    MenuOption,
    create_pdf_menu_options,
    validate_menu_selection,
    create_ocr_config_from_user_choices,
    detect_pdf_type_automatically
)

__all__ = [
    'cli_main',
    'interactive_main', 
    'InteractiveMenu',
    'MenuOption',
    'create_pdf_menu_options',
    'validate_menu_selection',
    'create_ocr_config_from_user_choices',
    'detect_pdf_type_automatically'
]