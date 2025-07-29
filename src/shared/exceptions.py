"""
Excepciones - ARCHIVO DE COMPATIBILIDAD.
Este archivo mantiene la compatibilidad mientras migramos.
"""

# Re-exportar desde domain
from domain.exceptions import (
    DomainError,
    ConfigurationError,
    OCRError,
    DocumentError,
    ProcessingError,
    StorageError
)

# Mantener nombres antiguos
DocumentNotFoundError = DocumentError
InvalidDocumentError = DocumentError
QualityThresholdError = ProcessingError

__all__ = [
    'DomainError',
    'ConfigurationError', 
    'OCRError',
    'DocumentError',
    'ProcessingError',
    'StorageError',
    'DocumentNotFoundError',
    'InvalidDocumentError',
    'QualityThresholdError'
]
