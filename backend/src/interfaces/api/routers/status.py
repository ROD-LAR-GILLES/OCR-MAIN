"""
Router para endpoints de estado del sistema.
"""
import os
import platform
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends

from interfaces.api.models.responses import SystemStatusResponse
from interfaces.api.dependencies import SystemConfigDep

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/", response_model=SystemStatusResponse)
async def get_system_status(system_config: SystemConfigDep):
    """
    Obtener estado del sistema OCR.
    
    Args:
        system_config: Configuración del sistema
    
    Returns:
        SystemStatusResponse: Estado del sistema
    """
    try:
        # Verificar directorios
        output_dir = Path(getattr(system_config, 'output_directory', './resultado'))
        storage_available = True
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            # Intentar escribir un archivo de prueba
            test_file = output_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
        except Exception:
            storage_available = False
        
        # Contar documentos procesados
        processed_docs = 0
        if output_dir.exists():
            processed_docs = len([d for d in output_dir.iterdir() if d.is_dir()])
        
        # Información del sistema
        system_info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "current_directory": str(Path.cwd()),
            "output_directory": str(output_dir),
            "output_directory_exists": output_dir.exists(),
        }
        
        # Estados de motores OCR (simplificado)
        ocr_engines = {
            "basic": True,  # Asumimos que siempre está disponible
            "tesseract": True,  # Se verificaría en el sistema real
            "opencv": True  # Se verificaría en el sistema real
        }
        
        # Estadísticas de procesamiento
        processing_stats = {
            "total_documents": processed_docs,
            "documents_today": 0,  # Se calcularía en el sistema real
            "average_processing_time": 0.0
        }
        
        return SystemStatusResponse(
            api_status="running",
            ocr_engines=ocr_engines,
            storage_available=storage_available,
            system_info=system_info,
            processing_stats=processing_stats
        )
        
    except Exception as e:
        # Estado degradado en caso de error
        return SystemStatusResponse(
            api_status="degraded",
            ocr_engines={"basic": False, "tesseract": False, "opencv": False},
            storage_available=False,
            system_info={"error": str(e)},
            processing_stats={"total_documents": 0, "documents_today": 0, "average_processing_time": 0.0}
        )


@router.get("/engines")
async def get_engine_status():
    """
    Obtener estado específico de los motores OCR.
    
    Returns:
        dict: Estado de cada motor OCR
    """
    engines = {}
    
    try:
        # Verificar Tesseract
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=5)
        engines['tesseract'] = {
            'available': result.returncode == 0,
            'version': result.stdout.split('\n')[0] if result.returncode == 0 else None
        }
    except Exception:
        engines['tesseract'] = {'available': False, 'error': 'Not installed or not accessible'}
    
    try:
        # Verificar OpenCV (básico)
        import cv2
        engines['opencv'] = {
            'available': True,
            'version': cv2.__version__
        }
    except ImportError:
        engines['opencv'] = {'available': False, 'error': 'Not installed'}
    
    # Motor básico siempre disponible
    engines['basic'] = {'available': True, 'version': '1.0.0'}
    
    return {
        "timestamp": datetime.now().isoformat(),
        "engines": engines
    }


@router.get("/storage")
async def get_storage_status(system_config: SystemConfigDep):
    """
    Obtener estado del almacenamiento.
    
    Args:
        system_config: Configuración del sistema
    
    Returns:
        dict: Estado del almacenamiento
    """
    output_dir = Path(getattr(system_config, 'output_directory', './resultado'))
    
    storage_info = {
        "output_directory": str(output_dir),
        "exists": output_dir.exists(),
        "writable": False,
        "documents": 0,
        "total_size": 0
    }
    
    try:
        # Verificar si es escribible
        output_dir.mkdir(parents=True, exist_ok=True)
        test_file = output_dir / ".test_write"
        test_file.write_text("test")
        test_file.unlink()
        storage_info["writable"] = True
        
        # Contar documentos y calcular tamaño
        if output_dir.exists():
            dirs = [d for d in output_dir.iterdir() if d.is_dir()]
            storage_info["documents"] = len(dirs)
            
            total_size = 0
            for item in output_dir.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
            storage_info["total_size"] = total_size
            storage_info["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
    except Exception as e:
        storage_info["error"] = str(e)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "storage": storage_info
    }