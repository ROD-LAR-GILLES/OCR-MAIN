"""
FastAPI main application for OCR Processing API
"""
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
import traceback

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# IMPORTS DIRECTOS (evitan import circular):
from interfaces.api.routers.documents import router as documents_router
from interfaces.api.routers.health import router as health_router  
from interfaces.api.routers.status import router as status_router
from interfaces.api.routers.system import router as system_router
from interfaces.api.routers.files import router as files_router

# Crear aplicación FastAPI
app = FastAPI(
    title="OCR Processing API",
    description="API para procesamiento de documentos PDF con OCR",
    version="2.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(status_router, prefix="/api/v1")
app.include_router(files_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")


# MANEJADOR DE EXCEPCIONES CORREGIDO
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador personalizado para HTTPException.
    """
    logger.error(f"HTTPException en {request.url}: {exc.detail}")
    
    # Retornar JSONResponse válida
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def custom_general_exception_handler(request: Request, exc: Exception):
    """
    Manejador personalizado para excepciones generales.
    """
    logger.error(f"Error interno del servidor: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Retornar JSONResponse válida
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "details": str(exc),
            "path": str(request.url)
        }
    )


# Evento de inicio
@app.on_event("startup")
async def startup_event():
    """Inicialización de la aplicación."""
    logger.info("Iniciando OCR Processing API v2.0.0")
    
    try:
        logger.info("Verificando configuración del sistema...")
        
        # Importar configuración
        from interfaces.api.dependencies.container import get_system_config
        
        config = get_system_config()
        logger.info("Configuración cargada correctamente")
        
        # Crear directorios necesarios
        from pathlib import Path
        
        # Directorio de salida
        output_dir = Path(getattr(config, 'output_directory', './resultado'))
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de salida: {output_dir}")
        
        # Directorio de entrada
        input_dir = Path(getattr(config, 'input_directory', './pdfs'))
        input_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de entrada: {input_dir}")
        
        logger.info("Directorios verificados/creados")
        logger.info("API iniciada correctamente")
        
    except Exception as e:
        logger.error(f"Error durante el inicio: {e}")
        raise


# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar la aplicación."""
    logger.info("Cerrando OCR Processing API")


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz de la API."""
    return {
        "message": "OCR Processing API v2.0.0",
        "status": "operational",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health"
    }


# Endpoint de información
@app.get("/api/v1/")
async def api_info():
    """Información de la API."""
    return {
        "name": "OCR Processing API",
        "version": "2.0.0",
        "description": "API para procesamiento de documentos PDF con OCR",
        "endpoints": {
            "health": "/api/v1/health",
            "files": "/api/v1/files",
            "documents": "/api/v1/documents", 
            "system": "/api/v1/system"
        }
    }