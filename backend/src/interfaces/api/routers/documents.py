"""
Router para endpoints relacionados con documentos.
"""
import logging
import tempfile
import os
from typing import List, Optional
from pathlib import Path as PathLib 

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import FileResponse

# Imports organizados por responsabilidad
from interfaces.api.models.common import EngineType, PDFType
from interfaces.api.models.responses import (
    ProcessDocumentResponse,
    DocumentListResponse,
    ProcessingStatus,
    ErrorResponse
)
from interfaces.api.dependencies.container import (
    DocumentProcessorDep, 
    SystemConfigDep, 
    MarkdownGeneratorDep
)

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


@router.post("/upload-and-process", response_model=ProcessDocumentResponse)
async def upload_and_process_document(
    background_tasks: BackgroundTasks,
    document_processor: DocumentProcessorDep,
    markdown_generator: MarkdownGeneratorDep,
    system_config: SystemConfigDep,
    file: UploadFile = File(..., description="Archivo PDF a procesar"),
    engine_type: EngineType = Form(default="auto", description="Motor OCR a utilizar"),
    language: str = Form(default="spa", description="Idioma para OCR"),
    dpi: int = Form(default=300, description="DPI para procesamiento", ge=72, le=600),
    extract_tables: bool = Form(default=True, description="Extraer tablas del documento"),
    output_format: str = Form(default="both", description="Formato de salida"),
    generate_summary: bool = Form(default=False, description="Generar resumen")
):
    """
    Subir y procesar un documento PDF con configuración manual.
    
    Permite especificar todos los parámetros de procesamiento incluyendo
    motor OCR, DPI, idioma y formato de salida.
    
    Args:
        background_tasks: Tareas en segundo plano
        document_processor: Procesador de documentos inyectado
        markdown_generator: Generador de Markdown inyectado
        system_config: Configuración del sistema inyectada
        file: Archivo PDF a procesar
        engine_type: Motor OCR (basic, opencv, auto)
        language: Código de idioma de 3 letras (spa, eng, etc.)
        dpi: Resolución para procesamiento (72-600)
        extract_tables: Si extraer tablas del documento
        output_format: Formato de salida (text, markdown, both)
        generate_summary: Si generar resumen del documento
    
    Returns:
        ProcessDocumentResponse: Resultado del procesamiento con metadatos
        
    Raises:
        HTTPException: 400 si el archivo no es PDF
        HTTPException: 500 si hay error en el procesamiento
    """
    try:
        # Validación de archivo
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos PDF"
            )
        
        # Manejo de archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            logger.info(f"Procesando documento {file.filename} con motor {engine_type}")
            
            # Ejecutar procesamiento OCR
            result = document_processor.execute(pdf_path=Path(temp_path))
            
            # Generar archivos de salida
            output_dir = Path(result.output_directory)
            files_generated = []
            
            # Generar archivo de texto
            if output_format in ["text", "both"]:
                text_file = output_dir / f"{result.name}.txt"
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(result.extracted_text)
                files_generated.append(str(text_file))
            
            # Generar archivo Markdown
            if output_format in ["markdown", "both"]:
                markdown_file = output_dir / f"{result.name}.md"
                
                document_metadata = {
                    'filename': file.filename,
                    'total_pages': result.total_pages,
                    'confidence_score': result.confidence_score,
                    'processing_time': result.processing_time,
                    'document_id': result.name,
                    'engine_type': engine_type,
                    'dpi': dpi,
                    'language': language,
                    'extract_tables': extract_tables
                }
                
                markdown_content = markdown_generator.generate_markdown(
                    extracted_text=result.extracted_text,
                    document_metadata=document_metadata,
                    tables=result.tables,
                    output_path=markdown_file
                )
                files_generated.append(str(markdown_file))
            
            # Generar resumen si se solicita
            if generate_summary:
                summary_file = output_dir / f"{result.name}_summary.md"
                summary_content = markdown_generator.generate_summary_markdown(
                    documents=[{
                        'filename': file.filename,
                        'total_pages': result.total_pages,
                        'confidence_score': result.confidence_score,
                        'processing_time': result.processing_time,
                        'status': 'completed'
                    }],
                    output_path=summary_file
                )
                files_generated.append(str(summary_file))
            
            # Crear respuesta estructurada
            response = ProcessDocumentResponse(
                document_id=result.name,
                filename=file.filename,
                status=ProcessingStatus.COMPLETED,
                extracted_text=result.extracted_text,
                total_pages=result.total_pages,
                confidence_score=result.confidence_score,
                processing_time=result.processing_time,
                output_directory=str(result.output_directory),
                tables_extracted=len(result.tables) if result.tables else 0,
                message=f"Documento procesado exitosamente. Archivos generados: {len(files_generated)}"
            )
            
            logger.info(f"Documento {file.filename} procesado exitosamente con formato {output_format}")
            return response
            
        finally:
            # Limpieza de recursos
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando documento {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando documento: {str(e)}"
        )


@router.post("/upload-auto", response_model=ProcessDocumentResponse)
async def upload_and_process_document_auto(
    background_tasks: BackgroundTasks,
    document_processor: DocumentProcessorDep,
    markdown_generator: MarkdownGeneratorDep,
    system_config: SystemConfigDep,
    file: UploadFile = File(..., description="Archivo PDF a procesar automáticamente"),
    language: str = Form(default="spa", description="Idioma para OCR"),
    output_format: str = Form(default="both", description="Formato de salida"),
    generate_summary: bool = Form(default=False, description="Generar resumen")
):
    """
    Procesar documento con detección automática de tipo y motor OCR.
    
    Analiza automáticamente el tipo de PDF (nativo/escaneado) y selecciona
    el motor OCR más apropiado junto con la configuración óptima.
    
    Args:
        background_tasks: Tareas en segundo plano
        document_processor: Procesador de documentos inyectado
        markdown_generator: Generador de Markdown inyectado
        system_config: Configuración del sistema inyectada
        file: Archivo PDF a procesar
        language: Código de idioma para OCR
        output_format: Formato de salida (text, markdown, both)
        generate_summary: Si generar resumen automático
    
    Returns:
        ProcessDocumentResponse: Resultado con información de detección automática
        
    Raises:
        HTTPException: 400 si el archivo no es PDF
        HTTPException: 500 si hay error en el procesamiento
    """
    try:
        # Validación de archivo
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos PDF"
            )
        
        # Guardar archivo temporalmente
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Detección automática de tipo de PDF
            from interfaces.cli.menu_utils import detect_pdf_type_automatically
            pdf_type = detect_pdf_type_automatically(temp_path)
            
            # Selección automática de motor y configuración
            if pdf_type == "scanned":
                engine_type = "opencv"
                dpi = 300
                extract_tables = True
                logger.info(f"PDF escaneado detectado - usando motor OpenCV con DPI 300")
            else:
                engine_type = "basic"  
                dpi = 150
                extract_tables = True
                logger.info(f"PDF nativo detectado - usando motor básico con DPI 150")
            
            # Procesamiento con configuración automática
            result = document_processor.execute(pdf_path=Path(temp_path))
            
            # Generación de archivos de salida
            output_dir = Path(result.output_directory)
            files_generated = []
            
            # Archivo de texto
            if output_format in ["text", "both"]:
                text_file = output_dir / f"{result.name}.txt"
                text_file.write_text(result.extracted_text, encoding='utf-8')
                files_generated.append(str(text_file))
            
            # Archivo Markdown
            if output_format in ["markdown", "both"]:
                markdown_file = output_dir / f"{result.name}.md"
                markdown_content = markdown_generator.generate_markdown(
                    extracted_text=result.extracted_text,
                    document_metadata={
                        'filename': file.filename,
                        'document_id': result.name,
                        'total_pages': result.total_pages,
                        'confidence_score': result.confidence_score,
                        'processing_time': result.processing_time,
                        'engine_type': engine_type,
                        'pdf_type': pdf_type,
                        'auto_detected': True,
                        'dpi': dpi,
                        'language': language
                    },
                    tables=result.tables,
                    output_path=markdown_file
                )
                files_generated.append(str(markdown_file))
            
            # Resumen automático
            if generate_summary:
                summary_file = output_dir / f"{result.name}_summary.md"
                summary_content = markdown_generator.generate_summary_markdown(
                    documents=[result],
                    output_path=summary_file
                )
                files_generated.append(str(summary_file))
            
            # Respuesta con información de detección automática
            response = ProcessDocumentResponse(
                document_id=result.name,
                filename=file.filename,
                status=ProcessingStatus.COMPLETED,
                extracted_text=result.extracted_text,
                total_pages=result.total_pages,
                confidence_score=result.confidence_score,
                processing_time=result.processing_time,
                output_directory=str(result.output_directory),
                tables_extracted=len(result.tables) if result.tables else 0,
                message=f"Documento procesado automáticamente. Tipo: {pdf_type}, Motor: {engine_type}. Archivos: {len(files_generated)}"
            )
            
            logger.info(f"Documento {file.filename} procesado automáticamente - Tipo: {pdf_type}, Motor: {engine_type}")
            return response
            
        finally:
            # Limpieza de archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en procesamiento automático {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en procesamiento automático: {str(e)}"
        )


@router.get("/download/{document_id}")
async def download_document_result(
    document_id: str = Path(..., description="ID único del documento a descargar")
):
    """
    Descargar resultado de un documento procesado.
    
    Busca y devuelve el archivo Markdown generado para el documento especificado.
    
    Args:
        document_id: Identificador único del documento
    
    Returns:
        FileResponse: Archivo Markdown del documento
        
    Raises:
        HTTPException: 404 si el documento no existe
        HTTPException: 500 si hay error en el acceso al archivo
    """
    try:
        # Buscar archivo en directorio de resultados
        resultado_dir = PathLib("./resultado") 
        md_file = resultado_dir / f"{document_id}.md"
        
        if md_file.exists():
            logger.info(f"Descargando documento {document_id}")
            return FileResponse(
                path=str(md_file),
                filename=f"{document_id}.md",
                media_type="text/markdown"
            )
        
        # Documento no encontrado
        logger.warning(f"Documento {document_id} no encontrado")
        raise HTTPException(
            status_code=404, 
            detail=f"Documento {document_id} no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al descargar documento {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al descargar documento: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    system_config: SystemConfigDep,
    limit: int = Query(default=10, description="Límite de resultados", ge=1, le=100),
    offset: int = Query(default=0, description="Offset para paginación", ge=0)
):
    """
    Listar documentos procesados con paginación.
    
    Retorna una lista paginada de todos los documentos que han sido procesados,
    incluyendo información sobre archivos generados y estado.
    
    Args:
        system_config: Configuración del sistema inyectada
        limit: Número máximo de documentos a retornar (1-100)
        offset: Número de documentos a omitir (para paginación)
    
    Returns:
        DocumentListResponse: Lista paginada de documentos con metadatos
        
    Raises:
        HTTPException: 500 si hay error accediendo al directorio
    """
    try:
        # Obtener directorio de salida
        output_dir = PathLib(getattr(system_config, 'output_directory', './resultado'))  
        
        if not output_dir.exists():
            logger.info("Directorio de salida no existe, retornando lista vacía")
            return DocumentListResponse(
                documents=[],
                total=0,
                limit=limit,
                offset=offset
            )
        
        # Listar directorios de documentos procesados
        document_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
        document_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Aplicar paginación
        total_documents = len(document_dirs)
        paginated_dirs = document_dirs[offset:offset + limit]
        
        # Construir información de documentos
        documents = []
        for doc_dir in paginated_dirs:
            try:
                # Analizar archivos en el directorio
                text_files = list(doc_dir.glob("*.txt"))
                markdown_files = list(doc_dir.glob("*.md"))
                image_files = list(doc_dir.glob("*.png"))
                table_files = list(doc_dir.glob("*_tables.csv"))
                
                doc_info = {
                    "document_id": doc_dir.name,
                    "filename": f"{doc_dir.name}.pdf",
                    "status": ProcessingStatus.COMPLETED,
                    "output_directory": str(doc_dir),
                    "processed_at": doc_dir.stat().st_mtime,
                    "has_text": len(text_files) > 0,
                    "has_images": len(image_files) > 0,
                    "has_tables": len(table_files) > 0,
                    "has_markdown": len(markdown_files) > 0
                }
                documents.append(doc_info)
                
            except Exception as e:
                logger.warning(f"Error procesando directorio {doc_dir.name}: {e}")
                continue
        
        logger.info(f"Listando {len(documents)} documentos (total: {total_documents})")
        
        return DocumentListResponse(
            documents=documents,
            total=total_documents,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listando documentos: {str(e)}"
        )
