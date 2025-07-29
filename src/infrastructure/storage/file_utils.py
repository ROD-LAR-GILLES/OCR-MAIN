"""
Utilidades para manipulación de archivos PDF - Capa de Infraestructura.
"""

from pathlib import Path
from typing import List
import logging

# Actualizar imports para nueva arquitectura
from domain.constants import SUPPORTED_PDF_EXTENSIONS
from domain.exceptions import DocumentNotFoundError, InvalidDocumentError

logger = logging.getLogger(__name__)


def discover_pdf_files(directory: Path) -> List[str]:
    """
    Lista archivos PDF en un directorio.
    
    """
    if not directory.exists():
        raise DocumentNotFoundError(f"El directorio {directory} no existe")
    
    if not directory.is_dir():
        raise InvalidDocumentError(f"{directory} no es un directorio")
    
    try:
        pdf_files = []
        for p in directory.glob("*.pdf"):
            if p.is_file() and _is_valid_pdf_file(p):
                pdf_files.append(p.name)
        
        logger.info(f"Encontrados {len(pdf_files)} archivos PDF en {directory}")
        return sorted(pdf_files)
        
    except PermissionError as e:
        raise InvalidDocumentError(f"Sin permisos para leer {directory}: {e}")


def validate_pdf_exists(directory: Path, filename: str) -> bool:
    """
    Verifica si existe un archivo PDF válido en el directorio.
    
    """
    try:
        file_path = directory / filename
        return (file_path.exists() and 
                file_path.is_file() and 
                _is_valid_pdf_file(file_path))
    except Exception as e:
        logger.warning(f"Error validando PDF {filename}: {e}")
        return False


def _is_valid_pdf_file(file_path: Path) -> bool:
    """
    Verifica si un archivo es un PDF válido.

    """
    # Verificar extensión
    if file_path.suffix.lower() not in SUPPORTED_PDF_EXTENSIONS:
        return False
    
    # Verificar tamaño mínimo (PDFs vacíos son ~1KB)
    if file_path.stat().st_size < 1024:
        return False
    
    # Verificar header PDF básico
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)
            return header.startswith(b'%PDF-')
    except Exception:
        return False


def get_file_info(file_path: Path) -> dict:
    """
    Devuelve información básica de un archivo.
    
    """
    if not file_path.exists():
        raise DocumentNotFoundError(f"El archivo {file_path} no existe")
    
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": stat.st_mtime,
        "is_readable": file_path.is_file(),
        "is_valid_pdf": _is_valid_pdf_file(file_path) if file_path.suffix.lower() == '.pdf' else False
    }


def ensure_directory_exists(directory: Path) -> None:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directorio asegurado: {directory}")
    except Exception as e:
        raise InvalidDocumentError(f"No se pudo crear directorio {directory}: {e}")
