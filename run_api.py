"""
Script para iniciar la API FastAPI del sistema OCR.
"""
import uvicorn
import argparse
import sys
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from interfaces.api.main import app


def main():
    """Función principal para iniciar la API."""
    parser = argparse.ArgumentParser(description="OCR Processing API Server")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host para bind del servidor (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Puerto para el servidor (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Habilitar auto-reload para desarrollo"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Número de workers (default: 1)"
    )
    parser.add_argument(
        "--log-level", 
        default="info", 
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Nivel de logging (default: info)"
    )
    parser.add_argument(
        "--access-log", 
        action="store_true", 
        help="Habilitar access logs"
    )
    
    args = parser.parse_args()
    
    # Configuración de uvicorn
    config = {
        "app": app,
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level,
        "access_log": args.access_log,
    }
    
    # Configuración específica para desarrollo vs producción
    if args.reload:
        config.update({
            "reload": True,
            "reload_dirs": ["src"],
            "reload_includes": ["*.py"],
        })
        print(f" Modo desarrollo: auto-reload habilitado")
    else:
        config.update({
            "workers": args.workers,
        })
        print(f" Modo producción: {args.workers} worker(s)")
    
    print(f" Iniciando servidor en http://{args.host}:{args.port}")
    print(f" Documentación en http://{args.host}:{args.port}/docs")
    print(f" ReDoc en http://{args.host}:{args.port}/redoc")
    
    # Iniciar servidor
    uvicorn.run(**config)


if __name__ == "__main__":
    main()