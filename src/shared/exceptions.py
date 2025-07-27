# shared/exceptions.py
"""
Excepciones específicas del dominio OCR.
"""


class OCRError(Exception):
    """Excepción base para errores de OCR."""
    pass


class DocumentNotFoundError(OCRError):
    """Error cuando no se encuentra el documento."""
    pass


class InvalidDocumentError(OCRError):
    """Error cuando el documento no es válido."""
    pass


class ProcessingError(OCRError):
    """Error durante el procesamiento del documento."""
    pass


class ConfigurationError(OCRError):
    """Error en la configuración del sistema."""
    pass


class QualityThresholdError(OCRError):
    """Error cuando la calidad está por debajo del umbral."""
    pass
