"""
Modelos de datos para gestión de archivos subidos.

Este módulo define las estructuras de datos utilizadas para representar
archivos PDF subidos a través de la API REST, incluyendo sus metadatos,
estado de procesamiento y configuraciones detectadas automáticamente.
"""

from typing import Optional, Literal, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from pathlib import Path
from enum import Enum
from .common import PDFType, EngineType, ProcessingStatus


class UploadedFile(BaseModel):
    """
    Modelo que representa un archivo PDF subido al sistema OCR.
    
    Esta clase encapsula toda la información necesaria para gestionar
    archivos durante el flujo de trabajo de procesamiento OCR, desde
    la subida inicial hasta el procesamiento final.
    """
    
    # Configuración del modelo (Pydantic v2)
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Path: str,
        },
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )
    
    file_id: str = Field(
        description="Identificador único del archivo (11 caracteres UUID4)",
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9\-_]+$"
    )
    
    filename: str = Field(
        description="Nombre del archivo en el sistema con prefijo único",
        min_length=1,
        max_length=255
    )
    
    original_filename: str = Field(
        description="Nombre original del archivo subido por el usuario",
        min_length=1,
        max_length=255
    )
    
    size_mb: float = Field(
        description="Tamaño del archivo en megabytes",
        ge=0,
        le=1000
    )
    
    upload_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora de subida en UTC (generada automáticamente)"
    )
    
    file_path: str = Field(
        description="Ruta completa del archivo en el sistema",
        min_length=1
    )
    
    pdf_type: PDFType = Field(
        default="unknown",
        description="Tipo de PDF detectado automáticamente"
    )
    
    recommended_engine: EngineType = Field(
        default="basic",
        description="Motor OCR recomendado basado en análisis"
    )
    
    status: ProcessingStatus = Field(
        default=ProcessingStatus.UPLOADED,
        description="Estado actual del procesamiento"
    )


class FileUploadResponse(BaseModel):
    """Response para subida de archivos."""
    file_id: str = Field(description="ID único del archivo subido")
    filename: str = Field(description="Nombre del archivo en el sistema")
    original_filename: str = Field(description="Nombre original del archivo")
    size_mb: float = Field(description="Tamaño del archivo en MB")
    upload_date: datetime = Field(description="Fecha de subida")
    pdf_type: PDFType = Field(description="Tipo de PDF detectado")
    recommended_engine: EngineType = Field(description="Motor OCR recomendado")
    status: ProcessingStatus = Field(description="Estado del archivo")
    message: str = Field(description="Mensaje descriptivo")


class FileListResponse(BaseModel):
    """Response para listado de archivos."""
    files: List[UploadedFile] = Field(description="Lista de archivos subidos")
    total: int = Field(description="Total de archivos")
    limit: int = Field(description="Límite aplicado")
    offset: int = Field(description="Offset aplicado")


class FileInfoResponse(BaseModel):
    """Response para información de archivo específico."""
    file_id: str = Field(description="ID único del archivo")
    filename: str = Field(description="Nombre del archivo")
    original_filename: str = Field(description="Nombre original")
    size_mb: float = Field(description="Tamaño en MB")
    upload_date: datetime = Field(description="Fecha de subida")
    file_path: str = Field(description="Ruta del archivo")
    pdf_type: PDFType = Field(description="Tipo de PDF")
    recommended_engine: EngineType = Field(description="Motor recomendado")
    status: ProcessingStatus = Field(description="Estado actual")


class ProcessResult(BaseModel):
    """Response para resultado de procesamiento."""
    file_id: str = Field(description="ID del archivo procesado")
    document_id: str = Field(description="ID del documento generado")
    status: str = Field(description="Estado del procesamiento")
    message: str = Field(description="Mensaje descriptivo")
    processing_time: float = Field(description="Tiempo de procesamiento en segundos")
    confidence_score: float = Field(description="Puntuación de confianza del OCR")
    total_pages: int = Field(description="Total de páginas procesadas")
    output_files: List[str] = Field(description="Lista de archivos generados")


class ProcessRequest(BaseModel):
    """Request para procesamiento de archivo."""
    engine_type: EngineType = Field(
        default="auto",
        description="Motor OCR a utilizar"
    )
    language: str = Field(
        default="spa",
        description="Idioma para OCR",
        pattern=r"^[a-z]{3}$"
    )
    dpi: int = Field(
        default=300,
        description="DPI para procesamiento",
        ge=72,
        le=600
    )
    extract_tables: bool = Field(
        default=True,
        description="Extraer tablas del documento"
    )
    output_format: str = Field(
        default="both",
        description="Formato de salida: 'text', 'markdown', 'both'"
    )
    generate_summary: bool = Field(
        default=False,
        description="Generar resumen del documento"
    )


class BatchUploadResponse(BaseModel):
    """Response para subida múltiple de archivos."""
    uploaded_files: List[FileUploadResponse] = Field(description="Archivos subidos exitosamente")
    failed_files: List[str] = Field(description="Archivos que fallaron")
    total_uploaded: int = Field(description="Total de archivos subidos")
    total_failed: int = Field(description="Total de archivos fallidos")
    message: str = Field(description="Mensaje general del proceso")


class FileDeleteResponse(BaseModel):
    """Response para eliminación de archivo."""
    file_id: str = Field(description="ID del archivo eliminado")
    filename: str = Field(description="Nombre del archivo eliminado")
    status: str = Field(description="Estado de la eliminación")
    message: str = Field(description="Mensaje descriptivo")
    files_removed: List[str] = Field(description="Archivos físicos eliminados")
