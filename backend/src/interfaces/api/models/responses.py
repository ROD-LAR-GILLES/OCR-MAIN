"""
Modelos Pydantic para responses de la API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .common import ProcessingStatus, EngineType


class ProcessDocumentResponse(BaseModel):
    """Response unificado para procesamiento de documento."""
    document_id: str = Field(description="ID único del documento")
    filename: str = Field(description="Nombre del archivo original")
    status: ProcessingStatus = Field(description="Estado del procesamiento")
    extracted_text: Optional[str] = Field(default=None, description="Texto extraído")
    total_pages: int = Field(default=0, description="Total de páginas procesadas")
    confidence_score: Optional[float] = Field(default=None, description="Puntuación de confianza del OCR")
    processing_time: Optional[float] = Field(default=None, description="Tiempo de procesamiento en segundos")
    output_directory: Optional[str] = Field(default=None, description="Directorio de salida")
    tables_extracted: int = Field(default=0, description="Número de tablas extraídas")
    message: str = Field(description="Mensaje descriptivo")
    created_at: datetime = Field(default_factory=datetime.now, description="Fecha de creación")


class DocumentInfo(BaseModel):
    """Información básica de un documento."""
    document_id: str = Field(description="ID único del documento")
    filename: str = Field(description="Nombre del archivo")
    status: ProcessingStatus = Field(description="Estado del procesamiento")
    output_directory: str = Field(description="Directorio de salida")
    processed_at: float = Field(description="Timestamp de procesamiento")
    has_text: bool = Field(description="Si tiene archivo de texto")
    has_images: bool = Field(description="Si tiene imágenes")
    has_tables: bool = Field(description="Si tiene tablas")


class DocumentListResponse(BaseModel):
    """Response para listado de documentos."""
    documents: List[DocumentInfo] = Field(description="Lista de documentos")
    total: int = Field(description="Total de documentos")
    limit: int = Field(description="Límite aplicado")
    offset: int = Field(description="Offset aplicado")


class DocumentResponse(BaseModel):
    """Response para documento procesado (alternativo)."""
    id: str = Field(description="ID único del documento")
    name: str = Field(description="Nombre del documento")
    source_path: str = Field(description="Ruta del archivo original")
    extracted_text: str = Field(description="Texto extraído")
    tables: List[Dict[str, Any]] = Field(description="Tablas extraídas")
    confidence: Optional[float] = Field(description="Confianza del OCR")
    processing_time: Optional[float] = Field(description="Tiempo de procesamiento")
    created_at: datetime = Field(description="Fecha de procesamiento")
    generated_files: List[str] = Field(description="Archivos generados")
    output_directory: str = Field(description="Directorio de salida")


class ProcessingStatusResponse(BaseModel):
    """Response para estado de procesamiento."""
    status: str = Field(description="Estado: 'processing', 'completed', 'error'")
    message: str = Field(description="Mensaje descriptivo")
    progress: Optional[float] = Field(description="Progreso 0-100")
    document: Optional[DocumentResponse] = None
    error_details: Optional[str] = None


class HealthResponse(BaseModel):
    """Response para health check."""
    status: str = Field(description="Estado del servicio")
    version: str = Field(description="Versión de la API")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del check")
    uptime: float = Field(description="Tiempo de actividad en segundos")
    services: Dict[str, str] = Field(default_factory=dict, description="Estado de servicios")


class SystemStatusResponse(BaseModel):
    """Response para estado del sistema."""
    api_status: str = Field(description="Estado de la API")
    ocr_engines: Dict[str, bool] = Field(description="Estado de motores OCR")
    storage_available: bool = Field(description="Si el almacenamiento está disponible")
    system_info: Dict[str, Any] = Field(description="Información del sistema")
    processing_stats: Dict[str, int] = Field(description="Estadísticas de procesamiento")
    ocr_engine: Optional[str] = Field(default=None, description="Motor OCR principal")
    available_languages: List[str] = Field(default_factory=list, description="Idiomas disponibles")
    processed_documents: int = Field(default=0, description="Documentos procesados")
    available_files: List[str] = Field(default_factory=list, description="Archivos disponibles")


class ErrorResponse(BaseModel):
    """Response para errores."""
    error: str = Field(description="Tipo de error")
    message: str = Field(description="Mensaje del error")
    detail: Optional[str] = Field(default=None, description="Detalle adicional")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Detalles estructurados")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp del error")


class ConfigurationResponse(BaseModel):
    """Response para configuración."""
    ocr_engine: str = Field(description="Motor OCR configurado")
    language: str = Field(description="Idioma configurado")
    dpi: int = Field(description="DPI configurado")
    output_directory: str = Field(description="Directorio de salida")
    available_engines: List[str] = Field(description="Motores disponibles")
    available_languages: List[str] = Field(description="Idiomas disponibles")


class ProcessingStatsResponse(BaseModel):
    """Response para estadísticas de procesamiento."""
    total_documents: int = Field(description="Total de documentos procesados")
    successful_processes: int = Field(description="Procesamientos exitosos")
    failed_processes: int = Field(description="Procesamientos fallidos")
    average_processing_time: float = Field(description="Tiempo promedio de procesamiento")
    total_pages_processed: int = Field(description="Total de páginas procesadas")
    total_text_extracted: int = Field(description="Total de caracteres extraídos")
    last_processed: Optional[datetime] = Field(default=None, description="Último procesamiento")


class UploadResponse(BaseModel):
    """Response para subida de archivos."""
    filename: str = Field(description="Nombre del archivo")
    file_size: int = Field(description="Tamaño del archivo en bytes")
    file_type: str = Field(description="Tipo de archivo")
    upload_id: str = Field(description="ID de la subida")
    message: str = Field(description="Mensaje descriptivo")
