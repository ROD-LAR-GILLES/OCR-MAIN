"""
Utilidades para manipulación de archivos PDF.
"""

from pathlib import Path
from typing import List


def discover_pdf_files(directory: Path) -> List[str]:
    """
    Lista archivos PDF en un directorio.
    """
    if not directory.exists():
        raise FileNotFoundError(f"El directorio {directory} no existe")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} no es un directorio")
    
    try:
        pdf_files = [p.name for p in directory.glob("*.pdf") if p.is_file()]
        return sorted(pdf_files)
    except PermissionError as e:
        raise PermissionError(f"Sin permisos para leer {directory}: {e}")


def validate_pdf_exists(directory: Path, filename: str) -> bool:
    """
    Verifica si existe un archivo PDF en el directorio.
    """
    file_path = directory / filename
    return file_path.exists() and file_path.is_file() and filename.endswith('.pdf')


def get_file_info(file_path: Path) -> dict:
    """
    Devuelve información básica de un archivo.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"El archivo {file_path} no existe")
    
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "modified": stat.st_mtime,
        "is_readable": file_path.is_file()
    }
