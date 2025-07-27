"""
Router para endpoints de health check.
"""
import platform
import time
from datetime import datetime

from fastapi import APIRouter

from interfaces.api.models.responses import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])

# Tiempo de inicio de la aplicación
start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check básico de la API.
    
    Returns:
        HealthResponse: Estado de salud de la API
    """
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.now(),
        uptime=uptime
    )


@router.get("/detailed")
async def detailed_health_check():
    """
    Health check detallado con información del sistema.
    
    Returns:
        dict: Información detallada del sistema
    """
    uptime = time.time() - start_time
    
    try:
        # Información básica del sistema sin psutil
        system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
            "system_info": system_info,
            "api_info": {
                "framework": "FastAPI",
                "docs_url": "/docs",
                "redoc_url": "/redoc",
                "openapi_url": "/openapi.json"
            }
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime,
            "error": str(e),
            "message": "Health check parcialmente exitoso"
        }


@router.get("/liveness")
async def liveness_probe():
    """
    Probe de liveness para Kubernetes/Docker.
    
    Returns:
        dict: Estado de liveness
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/readiness")
async def readiness_probe():
    """
    Probe de readiness para Kubernetes/Docker.
    
    Returns:
        dict: Estado de readiness
    """
    # Aquí podrías verificar dependencias externas
    # como base de datos, servicios externos, etc.
    
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "ok",
            "dependencies": "ok"
        }
    }