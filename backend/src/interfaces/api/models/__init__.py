"""
Módulo de modelos de la API.
"""

# Imports desde common (tipos compartidos)
from .common import (
    PDFType,
    EngineType, 
    ProcessingStatus,
    OutputFormat
)

# Imports desde requests (ya no OCREngineType)
from .requests import (
    ProcessDocumentRequest,
    # No importar OCREngineType - ya no existe
)

# Imports desde responses
from .responses import (
    ProcessDocumentResponse,
    DocumentInfo,
    HealthResponse,
    ErrorResponse
)

# Imports desde uploaded_file
from .uploaded_file import (
    UploadedFile,
    FileUploadResponse,
    FileListResponse,
    FileInfoResponse,
    ProcessResult,
    ProcessRequest,
    BatchUploadResponse,
    FileDeleteResponse
)

__all__ = [
    # Tipos comunes
    "PDFType",
    "EngineType", 
    "ProcessingStatus",
    "OutputFormat",
    
    # Requests
    "ProcessDocumentRequest",
    
    # Responses
    "ProcessDocumentResponse",
    "DocumentInfo", 
    "HealthResponse",
    "ErrorResponse",
    
    # Uploaded files
    "UploadedFile",
    "FileUploadResponse", 
    "FileListResponse",
    "FileInfoResponse",
    "ProcessResult",
    "ProcessRequest",
    "BatchUploadResponse",
    "FileDeleteResponse"
]