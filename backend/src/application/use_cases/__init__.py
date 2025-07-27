"""
Casos de uso de la aplicación.
"""

from .process_document import ProcessDocument
from .extract_document_text import ExtractDocumentTextUseCase
from .extract_tables import ExtractTablesUseCase
from .save_document import SaveDocumentUseCase

__all__ = [
    'ProcessDocument',
    'ExtractDocumentTextUseCase',
    'ExtractTablesUseCase',
    'SaveDocumentUseCase'
]