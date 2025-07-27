# shared/constants.py
"""
Constantes del sistema OCR.
"""

# Directorios por defecto
DEFAULT_PDF_DIR = "pdfs"
DEFAULT_OUTPUT_DIR = "resultado"

# Configuraciones OCR
DEFAULT_LANGUAGE = "spa"
DEFAULT_DPI = 300
DEFAULT_CONFIDENCE_THRESHOLD = 60.0

# Tipos de motor OCR
ENGINE_TYPE_BASIC = "basic"
ENGINE_TYPE_OPENCV = "opencv"

# Calidad
HIGH_QUALITY_THRESHOLD = 80.0
MEDIUM_QUALITY_THRESHOLD = 60.0

# Formatos soportados
SUPPORTED_PDF_EXTENSIONS = ['.pdf']

# Mensajes de error comunes
ERROR_FILE_NOT_FOUND = "Archivo no encontrado"
ERROR_INVALID_PDF = "Archivo PDF inválido"
ERROR_PROCESSING_FAILED = "Error en procesamiento"
ERROR_EMPTY_DOCUMENT = "Documento vacío"

# Mensajes de éxito
SUCCESS_PROCESSING_COMPLETE = "Procesamiento completado exitosamente"
