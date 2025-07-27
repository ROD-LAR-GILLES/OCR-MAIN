"""
Modelos Pydantic para requests de la API.
"""
from pydantic import BaseModel, Field
from typing import Optional
from .common import EngineType, OutputFormat, OCREngine


class ProcessDocumentRequest(BaseModel):
    """Request para procesamiento de documento."""
    engine_type: EngineType = Field(default="auto", description="Tipo de motor OCR")
    language: str = Field(default="spa", description="Idioma para OCR", pattern=r"^[a-z]{3}$")
    dpi: int = Field(default=300, description="DPI para procesamiento", ge=150, le=600)
    extract_tables: bool = Field(default=True, description="Si extraer tablas")
    output_format: OutputFormat = Field(default="both", description="Formato de salida")
    generate_summary: bool = Field(default=False, description="Si generar resumen")

    class Config:
        """Configuración del modelo."""
        json_schema_extra = {
            "example": {
                "engine_type": "auto",
                "language": "spa",
                "dpi": 300,
                "extract_tables": True,
                "output_format": "both",
                "generate_summary": False
            }
        }


class DocumentListRequest(BaseModel):
    """Request para listado de documentos."""
    limit: int = Field(default=10, description="Límite de resultados", ge=1, le=100)
    offset: int = Field(default=0, description="Offset para paginación", ge=0)
    status_filter: Optional[str] = Field(default=None, description="Filtrar por estado")
    format_filter: Optional[OutputFormat] = Field(default=None, description="Filtrar por formato")


class DownloadRequest(BaseModel):
    """Request para descarga de archivos."""
    format_type: str = Field(description="Tipo de formato (text, markdown, tables, images)")
    include_metadata: bool = Field(default=True, description="Incluir metadatos en la descarga")


class ConfigurationRequest(BaseModel):
    """Request para configuración del sistema."""
    ocr_engine: Optional[OCREngine] = Field(default=None, description="Motor OCR a configurar")
    language: Optional[str] = Field(default=None, description="Idioma por defecto")
    dpi: Optional[int] = Field(default=None, description="DPI por defecto", ge=150, le=600)
    output_directory: Optional[str] = Field(default=None, description="Directorio de salida")
    enable_markdown_output: Optional[bool] = Field(default=None, description="Habilitar salida Markdown")
    markdown_template: Optional[str] = Field(default=None, description="Template de Markdown")


class HealthCheckRequest(BaseModel):
    """Request para health check."""
    include_detailed: bool = Field(default=False, description="Incluir información detallada")
    check_dependencies: bool = Field(default=True, description="Verificar dependencias")


class ProcessingStatusRequest(BaseModel):
    """Request para estado de procesamiento."""
    document_id: str = Field(description="ID del documento")
    include_logs: bool = Field(default=False, description="Incluir logs de procesamiento")
