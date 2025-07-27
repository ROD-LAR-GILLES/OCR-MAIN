"""
Router para gestión del sistema OCR.
Proporciona las mismas funcionalidades que el menú CLI.
"""
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict

from ..dependencies.container import SystemConfigDep
from interfaces.api.models.responses import SystemStatusResponse
from interfaces.api.models.uploaded_file import PDFType, EngineType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["system"])


def get_available_languages():
    """
    Obtener idiomas disponibles para OCR.
    """
    return {
        "spa": "Español",
        "eng": "Inglés", 
        "por": "Portugués",
        "fra": "Francés",
        "deu": "Alemán",
        "ita": "Italiano"
    }


def detect_pdf_type_automatically(file_path):
    """
    Detectar tipo de PDF automáticamente.
    Fallback simple si no existe la función original.
    """
    try:
        # Intentar importar la función original
        from ...cli.menu_utils import detect_pdf_type_automatically as original_detect
        return original_detect(file_path)
    except ImportError:
        # Fallback simple
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) > 0:
                    page = pdf.pages[0]
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        return "native"
                    else:
                        return "scanned"
                return "unknown"
        except Exception:
            return "unknown"


# Modelos de respuesta
class SystemStatusResponse(BaseModel):
    """Respuesta del estado del sistema."""
    status: str
    version: str
    tesseract_available: bool
    opencv_available: bool
    current_config: dict
    directories: dict
    statistics: dict


class QualityProfile(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    """Perfil de calidad OCR."""
    name: str = Field(description="Nombre único del perfil")
    description: str = Field(description="Descripción detallada")
    dpi: int
    confidence_threshold: float
    tesseract_config: str
    recommended_for: str


class AvailableFile(BaseModel):
    """Archivo PDF disponible para procesar."""
    filename: str
    filepath: str
    size_mb: float
    modified_date: datetime
    pdf_type: Optional[str] = None
    recommended_engine: Optional[str] = None


class ProcessedDocument(BaseModel):
    """Documento procesado."""
    document_id: str
    filename: str
    processed_date: datetime
    confidence_score: float
    total_pages: int
    engine_used: str
    output_files: List[str]
    size_mb: float


class SystemConfigUpdate(BaseModel):
    """Actualización de configuración del sistema."""
    output_directory: Optional[str] = None
    input_directory: Optional[str] = None
    default_language: Optional[str] = None
    default_dpi: Optional[int] = None
    confidence_threshold: Optional[float] = None
    quality_profile: Optional[str] = None


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(config: SystemConfigDep):
    """
    Obtener estado completo del sistema.
    Equivalente a 'Ver estado del sistema' en CLI.
    """
    try:
        # Verificar disponibilidad de componentes
        tesseract_available = True
        opencv_available = True
        
        try:
            import cv2
        except ImportError:
            opencv_available = False
            
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
        except:
            tesseract_available = False
        
        # Obtener estadísticas de procesamiento
        output_dir = Path(getattr(config, 'output_directory', './resultado'))
        processed_docs = len(list(output_dir.glob('*.md'))) if output_dir.exists() else 0
        
        input_dir = Path(getattr(config, 'input_directory', './pdfs'))
        available_docs = len(list(input_dir.glob('*.pdf'))) if input_dir.exists() else 0
        
        # Calcular tamaño total de archivos procesados
        total_size = 0
        if output_dir.exists():
            for file in output_dir.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
        
        return SystemStatusResponse(
            status="operational" if tesseract_available else "limited",
            version="2.0.0",
            tesseract_available=tesseract_available,
            opencv_available=opencv_available,
            current_config={
                "output_directory": getattr(config, 'output_directory', './resultado'),
                "input_directory": getattr(config, 'input_directory', './pdfs'),
                "default_language": getattr(config, 'default_language', 'spa'),
                "default_dpi": getattr(config, 'default_dpi', 300),
                "confidence_threshold": getattr(config, 'confidence_threshold', 60.0),
                "tesseract_config": getattr(config, 'tesseract_config', '--oem 3 --psm 6')
            },
            directories={
                "input_exists": input_dir.exists(),
                "output_exists": output_dir.exists(),
                "logs_directory": getattr(config, 'logs_directory', './logs')
            },
            statistics={
                "documents_processed": processed_docs,
                "documents_available": available_docs,
                "total_output_size_mb": round(total_size / (1024 * 1024), 2)
            }
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.get("/profiles", response_model=List[QualityProfile])
async def get_quality_profiles():
    """
    Obtener perfiles de calidad disponibles.
    Equivalente a opciones de configuración en CLI.
    """
    profiles = [
        QualityProfile(
            name="fast",
            description="Procesamiento rápido para documentos de alta calidad",
            dpi=150,
            confidence_threshold=50.0,
            tesseract_config="--oem 3 --psm 6",
            recommended_for="PDFs nativos, documentos escaneados de alta calidad"
        ),
        QualityProfile(
            name="balanced",
            description="Configuración balanceada para uso general",
            dpi=300,
            confidence_threshold=60.0,
            tesseract_config="--oem 3 --psm 6",
            recommended_for="La mayoría de documentos"
        ),
        QualityProfile(
            name="high",
            description="Alta precisión para documentos difíciles",
            dpi=600,
            confidence_threshold=80.0,
            tesseract_config="--oem 3 --psm 8",
            recommended_for="Documentos escaneados de baja calidad, textos pequeños"
        ),
        QualityProfile(
            name="custom",
            description="Configuración personalizada",
            dpi=300,
            confidence_threshold=60.0,
            tesseract_config="--oem 3 --psm 6",
            recommended_for="Configuración manual según necesidades específicas"
        )
    ]
    return profiles


@router.get("/files/available", response_model=List[AvailableFile])
async def list_available_files(
    config: SystemConfigDep,
    analyze_type: bool = Query(False, description="Analizar tipo de PDF y motor recomendado")
):
    """
    Listar archivos PDF disponibles para procesar.
    Equivalente a 'Listar archivos disponibles' en CLI.
    """
    try:
        input_dir = Path(getattr(config, 'input_directory', './pdfs'))
        
        if not input_dir.exists():
            return []
        
        files = []
        for pdf_file in input_dir.glob('*.pdf'):
            try:
                stat = pdf_file.stat()
                
                file_info = AvailableFile(
                    filename=pdf_file.name,
                    filepath=str(pdf_file),
                    size_mb=round(stat.st_size / (1024 * 1024), 2),
                    modified_date=datetime.fromtimestamp(stat.st_mtime)
                )
                
                # Análisis opcional del tipo de PDF
                if analyze_type:
                    try:
                        pdf_type = detect_pdf_type_automatically(str(pdf_file))
                        file_info.pdf_type = pdf_type
                        file_info.recommended_engine = "opencv" if pdf_type == "scanned" else "basic"
                    except Exception as e:
                        logger.warning(f"No se pudo analizar {pdf_file.name}: {e}")
                        file_info.pdf_type = "unknown"
                        file_info.recommended_engine = "basic"
                
                files.append(file_info)
                
            except Exception as e:
                logger.warning(f"Error procesando archivo {pdf_file.name}: {e}")
                continue
        
        # Ordenar por fecha de modificación (más reciente primero)
        files.sort(key=lambda x: x.modified_date, reverse=True)
        
        return files
        
    except Exception as e:
        logger.error(f"Error listando archivos disponibles: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando archivos: {str(e)}")


@router.get("/files/processed", response_model=List[ProcessedDocument])
async def list_processed_documents(
    config: SystemConfigDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    engine_filter: Optional[str] = Query(None, description="Filtrar por motor OCR usado"),
    min_confidence: Optional[float] = Query(None, ge=0, le=100, description="Confianza mínima")
):
    """
    Listar documentos procesados con filtros avanzados.
    Equivalente a 'Ver resultados anteriores' en CLI.
    """
    try:
        output_dir = Path(getattr(config, 'output_directory', './resultado'))
        
        if not output_dir.exists():
            return []
        
        documents = []
        
        # Buscar archivos markdown procesados
        for md_file in output_dir.glob('*.md'):
            try:
                # Leer metadatos del archivo markdown
                content = md_file.read_text(encoding='utf-8')
                
                # Extraer información básica
                document_id = md_file.stem
                
                # Parsear metadatos del markdown
                confidence = 0.0
                engine = "unknown"
                pages = 1
                filename = md_file.name
                
                # Extraer datos del contenido markdown
                lines = content.split('\n')
                for line in lines:
                    if '**Confianza OCR**:' in line:
                        try:
                            conf_str = line.split(':', 1)[1].strip().replace('%', '').replace('*', '')
                            confidence = float(conf_str) / 100 if float(conf_str) > 1 else float(conf_str)
                        except:
                            pass
                    elif '**Motor OCR**:' in line:
                        engine = line.split(':', 1)[1].strip().replace('*', '').lower()
                    elif '**Páginas Procesadas**:' in line:
                        try:
                            pages = int(line.split(':', 1)[1].strip().replace('*', ''))
                        except:
                            pass
                    elif '**Archivo Original**:' in line:
                        filename = line.split(':', 1)[1].strip().replace('*', '')
                
                # Aplicar filtros
                if engine_filter and engine_filter.lower() not in engine:
                    continue
                    
                if min_confidence and confidence < min_confidence / 100:
                    continue
                
                # Buscar archivos relacionados
                base_name = document_id
                output_files = []
                for ext in ['.md', '.txt', '.json']:
                    related_file = output_dir / f"{base_name}{ext}"
                    if related_file.exists():
                        output_files.append(f"{base_name}{ext}")
                
                # Buscar CSV de tablas
                for csv_file in output_dir.glob(f"{base_name}*tables*.csv"):
                    output_files.append(csv_file.name)
                
                stat = md_file.stat()
                
                doc = ProcessedDocument(
                    document_id=document_id,
                    filename=filename,
                    processed_date=datetime.fromtimestamp(stat.st_mtime),
                    confidence_score=confidence * 100,  # Convertir a porcentaje
                    total_pages=pages,
                    engine_used=engine,
                    output_files=output_files,
                    size_mb=round(stat.st_size / (1024 * 1024), 2)
                )
                
                documents.append(doc)
                
            except Exception as e:
                logger.warning(f"Error procesando documento {md_file.name}: {e}")
                continue
        
        # Ordenar por fecha de procesamiento (más reciente primero)
        documents.sort(key=lambda x: x.processed_date, reverse=True)
        
        # Aplicar paginación
        total = len(documents)
        paginated = documents[offset:offset + limit]
        
        return paginated
        
    except Exception as e:
        logger.error(f"Error listando documentos procesados: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando documentos: {str(e)}")


@router.post("/config/update")
async def update_system_config(
    config_update: SystemConfigUpdate,
    config: SystemConfigDep
):
    """
    Actualizar configuración del sistema.
    Equivalente a 'Configurar sistema' en CLI.
    """
    try:
        updated_fields = []
        
        # Actualizar campos modificados
        if config_update.output_directory:
            config.output_directory = config_update.output_directory
            Path(config_update.output_directory).mkdir(parents=True, exist_ok=True)
            updated_fields.append("output_directory")
            
        if config_update.input_directory:
            config.input_directory = config_update.input_directory
            Path(config_update.input_directory).mkdir(parents=True, exist_ok=True)
            updated_fields.append("input_directory")
            
        if config_update.default_language:
            available_langs = list(get_available_languages().keys())
            if config_update.default_language not in available_langs:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Idioma no disponible. Idiomas soportados: {', '.join(available_langs)}"
                )
            config.default_language = config_update.default_language
            updated_fields.append("default_language")
            
        if config_update.default_dpi:
            if not 72 <= config_update.default_dpi <= 600:
                raise HTTPException(status_code=400, detail="DPI debe estar entre 72 y 600")
            config.default_dpi = config_update.default_dpi
            updated_fields.append("default_dpi")
            
        if config_update.confidence_threshold:
            if not 0 <= config_update.confidence_threshold <= 100:
                raise HTTPException(status_code=400, detail="Umbral de confianza debe estar entre 0 y 100")
            config.confidence_threshold = config_update.confidence_threshold
            updated_fields.append("confidence_threshold")
        
        # Aplicar perfil de calidad si se especifica
        if config_update.quality_profile:
            profiles = {
                "fast": {"dpi": 150, "confidence_threshold": 50.0},
                "balanced": {"dpi": 300, "confidence_threshold": 60.0},
                "high": {"dpi": 600, "confidence_threshold": 80.0}
            }
            
            if config_update.quality_profile in profiles:
                profile = profiles[config_update.quality_profile]
                config.default_dpi = profile["dpi"]
                config.confidence_threshold = profile["confidence_threshold"]
                updated_fields.extend(["default_dpi", "confidence_threshold"])
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Perfil no válido. Perfiles disponibles: {', '.join(profiles.keys())}"
                )
        
        logger.info(f"Configuración actualizada: {', '.join(updated_fields)}")
        
        return {
            "message": "Configuración actualizada exitosamente",
            "updated_fields": updated_fields,
            "current_config": {
                "output_directory": config.output_directory,
                "input_directory": config.input_directory,
                "default_language": config.default_language,
                "default_dpi": config.default_dpi,
                "confidence_threshold": config.confidence_threshold
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando configuración: {str(e)}")


@router.get("/languages")
async def get_available_languages_endpoint():
    """Obtener idiomas disponibles para OCR."""
    try:
        return get_available_languages()
    except Exception as e:
        logger.error(f"Error obteniendo idiomas: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo idiomas: {str(e)}")