"""
Router para gestión de archivos subidos y procesamiento diferido.
"""
import logging
import os
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
import shutil

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse

from interfaces.api.models.uploaded_file import UploadedFile
from interfaces.api.dependencies.container import (
    get_document_processor, 
    get_system_config,
    get_markdown_generator,
    DocumentProcessorDep,
    SystemConfigDep,
    MarkdownGeneratorDep,
    FileManagerDep
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])


# Modelos
class UploadedFile(BaseModel):
    """Archivo subido al sistema."""
    file_id: str
    filename: str
    original_filename: str
    size_mb: float
    upload_date: datetime
    file_path: str
    pdf_type: Optional[str] = None
    recommended_engine: Optional[str] = None
    status: str = "uploaded"  # uploaded, processing, processed, error


class ProcessRequest(BaseModel):
    """Solicitud de procesamiento de archivo."""
    engine_type: str = "auto"  # auto, basic, opencv
    language: str = "spa"
    dpi: int = 300
    extract_tables: bool = True
    output_format: str = "both"  # text, markdown, both
    generate_summary: bool = False


class ProcessResult(BaseModel):
    """Resultado del procesamiento."""
    file_id: str
    document_id: str
    status: str
    message: str
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    total_pages: Optional[int] = None
    output_files: List[str] = []


# Almacenamiento en memoria (en producción usar base de datos)
uploaded_files_db = {}


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

@router.get("/", response_model=List[UploadedFile])
async def list_uploaded_files(
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    Listar archivos subidos.
    """
    try:
        files = list(uploaded_files_db.values())
        
        # Aplicar filtro de estado
        if status_filter:
            files = [f for f in files if f.status == status_filter]
        
        # Ordenar por fecha de subida (más reciente primero)
        files.sort(key=lambda x: x.upload_date, reverse=True)
        
        # Aplicar paginación
        paginated = files[offset:offset + limit]
        
        return paginated
        
    except Exception as e:
        logger.error(f"Error listando archivos: {e}")
        raise HTTPException(status_code=500, detail=f"Error listando archivos: {str(e)}")


@router.get("/{file_id}", response_model=UploadedFile)
async def get_file_info(file_id: str):
    """
    Obtener información de un archivo específico.
    """
    if file_id not in uploaded_files_db:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return uploaded_files_db[file_id]


@router.post("/{file_id}/process", response_model=ProcessResult)
async def process_uploaded_file(
    file_id: str,
    process_request: ProcessRequest,
    background_tasks: BackgroundTasks,
    document_processor: DocumentProcessorDep,
    markdown_generator: MarkdownGeneratorDep,
    config: SystemConfigDep
):
    """
    Procesar un archivo previamente subido.
    """
    try:
        # Verificar que el archivo existe
        if file_id not in uploaded_files_db:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        uploaded_file = uploaded_files_db[file_id]
        
        # Verificar que el archivo físico existe
        if not Path(uploaded_file.file_path).exists():
            raise HTTPException(status_code=404, detail="Archivo físico no encontrado")
        
        # Marcar como procesando
        uploaded_file.status = "processing"
        uploaded_files_db[file_id] = uploaded_file
        
        # Determinar motor OCR
        engine_type = process_request.engine_type
        if engine_type == "auto":
            if uploaded_file.pdf_type == "scanned":
                engine_type = "opencv"
            else:
                engine_type = "basic"
        
        logger.info(f"Procesando archivo {uploaded_file.filename} con motor {engine_type}")
        
        # Procesar documento
        result = document_processor.execute(pdf_path=Path(uploaded_file.file_path))
        
        # Debug temporal
        logger.info(f"Document attributes: {dir(result)}")
        logger.info(f"Document type: {type(result)}")
        
        # Generar archivos de salida
        files_generated = []
        
        if process_request.output_format in ["text", "both"]:
            # Generar archivo de texto
            text_file = Path(result.output_directory) / f"{result.name}.txt"
            text_file.write_text(result.extracted_text, encoding='utf-8')
            files_generated.append(f"{result.name}.txt")
        
        if process_request.output_format in ["markdown", "both"]:
            # Generar Markdown
            markdown_content = markdown_generator.generate_markdown(
                extracted_text=result.extracted_text,
                document_metadata={
                    'filename': uploaded_file.original_filename,
                    'document_id': result.name, 
                    'total_pages': 1, 
                    'confidence_score': result.confidence, 
                    'processing_time': result.processing_time,
                    'engine_type': engine_type,
                    'pdf_type': uploaded_file.pdf_type,
                    'file_id': file_id
                },
                tables=result.tables,
                output_path=Path(result.output_directory) / f"{result.name}.md"
            )
            files_generated.append(f"{result.name}.md")
        
        # Generar resumen si se solicita
        if process_request.generate_summary:
            summary_content = markdown_generator.generate_summary_markdown(
                documents=[result],
                output_path=Path(result.output_directory) / f"{result.name}_summary.md"
            )
            files_generated.append(f"{result.name}_summary.md")
        
        # Calcular total_pages si es necesario
        try:
            import fitz  # PyMuPDF
            with fitz.open(uploaded_file.file_path) as doc:
                total_pages = len(doc)
        except:
            total_pages = 1
        
        # Marcar como procesado
        uploaded_file.status = "processed"
        uploaded_files_db[file_id] = uploaded_file
        
        # Crear respuesta
        process_result = ProcessResult(
            file_id=file_id,
            document_id=result.name, 
            status="completed",
            message=f"Procesado con motor {engine_type}. {len(files_generated)} archivos generados.",
            processing_time=result.processing_time,
            confidence_score=result.confidence, 
            total_pages=total_pages, 
            output_files=files_generated
        )
        
        logger.info(f"Archivo {uploaded_file.filename} procesado exitosamente. ID documento: {result.name}")
        return process_result
        
    except HTTPException:
        # Marcar como error
        if file_id in uploaded_files_db:
            uploaded_files_db[file_id].status = "error"
        raise
    except Exception as e:
        # Marcar como error
        if file_id in uploaded_files_db:
            uploaded_files_db[file_id].status = "error"
        
        logger.error(f"Error procesando archivo {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")


@router.delete("/{file_id}")
async def delete_uploaded_file(file_id: str):
    """
    Eliminar archivo subido.
    """
    try:
        if file_id not in uploaded_files_db:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        
        uploaded_file = uploaded_files_db[file_id]
        
        # Eliminar archivo físico si existe
        file_path = Path(uploaded_file.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Eliminar de la base de datos
        del uploaded_files_db[file_id]
        
        logger.info(f"Archivo {uploaded_file.filename} eliminado")
        return {"message": f"Archivo {uploaded_file.filename} eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando archivo {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando archivo: {str(e)}")


@router.post("/batch-upload", response_model=List[UploadedFile])
async def batch_upload_files(
    config: SystemConfigDep,
    files: List[UploadFile] = File(...),
    analyze_type: bool = Form(True)
):
    """
    Subir múltiples archivos PDF.
    """
    try:
        uploaded_files = []
        
        for file in files:
            try:
                # Validar archivo
                if not file.filename.lower().endswith('.pdf'):
                    logger.warning(f"Archivo {file.filename} omitido: no es PDF")
                    continue
                
                # Procesar cada archivo individualmente
                # Generar ID único para el archivo
                file_id = str(uuid.uuid4())[:12]
                
                # Crear directorio de archivos subidos
                upload_dir = Path(getattr(config, 'input_directory', './pdfs'))
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                # Guardar archivo con nombre único
                unique_filename = f"{file_id}_{file.filename}"
                file_path = upload_dir / unique_filename
                
                # Escribir archivo
                content = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                
                # Crear registro del archivo
                uploaded_file = UploadedFile(
                    file_id=file_id,
                    filename=unique_filename,
                    original_filename=file.filename,
                    size_mb=round(len(content) / (1024 * 1024), 2),
                    upload_date=datetime.now(),
                    file_path=str(file_path),
                    status="uploaded"
                )
                
                # Análisis opcional del tipo de PDF
                if analyze_type:
                    try:
                        pdf_type = detect_pdf_type_automatically(str(file_path))
                        uploaded_file.pdf_type = pdf_type
                        uploaded_file.recommended_engine = "opencv" if pdf_type == "scanned" else "basic"
                        logger.info(f"Archivo {file.filename} analizado: tipo {pdf_type}")
                    except Exception as e:
                        logger.warning(f"No se pudo analizar {file.filename}: {e}")
                        uploaded_file.pdf_type = "unknown"
                        uploaded_file.recommended_engine = "basic"
                
                # Guardar en "base de datos"
                uploaded_files_db[file_id] = uploaded_file
                uploaded_files.append(uploaded_file)
                
                logger.info(f"Archivo {file.filename} subido con ID {file_id}")
                
            except Exception as e:
                logger.error(f"Error subiendo {file.filename}: {e}")
                continue
        
        logger.info(f"Subida en lote completada: {len(uploaded_files)} archivos subidos")
        return uploaded_files
        
    except Exception as e:
        logger.error(f"Error en subida en lote: {e}")
        raise HTTPException(status_code=500, detail=f"Error en subida en lote: {str(e)}")
    

@router.post("/upload", response_model=UploadedFile)
async def upload_file(
    config: SystemConfigDep,
    file: UploadFile = File(...),
    analyze_type: bool = Form(True)
):
    """
    Subir archivo PDF sin procesarlo.
    """
    try:
        # Validar tipo de archivo
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        
        # Generar ID único para el archivo
        file_id = str(uuid.uuid4())[:12]
        
        # Crear directorio de archivos subidos
        upload_dir = Path(getattr(config, 'input_directory', './pdfs'))
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivo con nombre único
        unique_filename = f"{file_id}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        # Escribir archivo
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Crear registro del archivo
        uploaded_file = UploadedFile(
            file_id=file_id,
            filename=unique_filename,
            original_filename=file.filename,
            size_mb=round(len(content) / (1024 * 1024), 2),
            upload_date=datetime.now(),
            file_path=str(file_path),
            status="uploaded"
        )
        
        # Análisis opcional del tipo de PDF
        if analyze_type:
            try:
                pdf_type = detect_pdf_type_automatically(str(file_path))
                uploaded_file.pdf_type = pdf_type
                uploaded_file.recommended_engine = "opencv" if pdf_type == "scanned" else "basic"
                logger.info(f"Archivo {file.filename} analizado: tipo {pdf_type}")
            except Exception as e:
                logger.warning(f"No se pudo analizar {file.filename}: {e}")
                uploaded_file.pdf_type = "unknown"
                uploaded_file.recommended_engine = "basic"
        
        # Guardar en "base de datos"
        uploaded_files_db[file_id] = uploaded_file
        
        logger.info(f"Archivo {file.filename} subido con ID {file_id}")
        return uploaded_file
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error subiendo archivo: {str(e)}")
