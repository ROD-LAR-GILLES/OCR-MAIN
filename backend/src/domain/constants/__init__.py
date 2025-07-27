"""
Constantes del dominio OCR.
"""

# Tipos de motor OCR
ENGINE_TYPE_BASIC = "basic"
ENGINE_TYPE_OPENCV = "opencv"

# Configuraciones por defecto
DEFAULT_LANGUAGE = "spa"
DEFAULT_DPI = 300
DEFAULT_CONFIDENCE_THRESHOLD = 60.0

# Umbrales de calidad
HIGH_QUALITY_THRESHOLD = 80.0
MEDIUM_QUALITY_THRESHOLD = 60.0

# Formatos soportados
SUPPORTED_PDF_EXTENSIONS = ['.pdf']

# Directorios por defecto
DEFAULT_PDF_DIR = "pdfs"
DEFAULT_OUTPUT_DIR = "resultado"