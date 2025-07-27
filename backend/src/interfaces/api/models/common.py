"""
Tipos y enums comunes para la API.
"""

from enum import Enum
from typing import Literal

# Tipos unificados
PDFType = Literal["native", "scanned", "mixed", "unknown"]
EngineType = Literal["basic", "opencv", "auto"]
OutputFormat = Literal["text", "markdown", "both"]

class ProcessingStatus(str, Enum):
    """Estados de procesamiento unificados."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"
    UPLOADED = "uploaded"

class OCREngine(str, Enum):  # ← AGREGAR ESTA CLASE
    """Motores OCR disponibles."""
    AUTO = "auto"
    BASIC = "basic"
    OPENCV = "opencv"
    TESSERACT = "tesseract"