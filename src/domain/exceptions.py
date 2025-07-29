"""
Excepciones específicas del dominio OCR.
Define la jerarquía de excepciones para el sistema.
"""

class DomainError(Exception):
    """Excepción base para todos los errores del dominio."""
    pass


class ConfigurationError(DomainError):
    """Error en la configuración del sistema."""
    pass


class OCRError(DomainError):
    """Error base para operaciones OCR."""
    pass


class DocumentError(DomainError):
    """Error relacionado con documentos."""
    pass


class ProcessingError(DomainError):
    """Error durante el procesamiento."""
    pass


class StorageError(DomainError):
    """Error en operaciones de almacenamiento."""
    pass

# Mantener compatibilidad con ubicación anterior
DocumentNotFoundError = DocumentError
InvalidDocumentError = DocumentError
QualityThresholdError = ProcessingError