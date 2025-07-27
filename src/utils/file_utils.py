"""
Utilidades para manipulación de archivos.

Funciones puras para operaciones de archivos sin dependencias de I/O específico.
"""

from pathlib import Path
from typing import List


def discover_pdf_files(directory: Path) -> List[str]:
    """
    Descubre y lista archivos PDF en un directorio.
    
    Args:
        directory: Directorio donde buscar archivos PDF
        
    Returns:
        Lista ordenada de nombres de archivos PDF encontrados
        
    Raises:
        FileNotFoundError: Si el directorio no existe
        PermissionError: Si no hay permisos para leer el directorio
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
    Valida que un archivo PDF específico existe en el directorio.
    
    Args:
        directory: Directorio donde buscar el archivo
        filename: Nombre del archivo PDF a validar
        
    Returns:
        True si el archivo existe, False en caso contrario
    """
    file_path = directory / filename
    return file_path.exists() and file_path.is_file() and filename.endswith('.pdf')


def get_file_info(file_path: Path) -> dict:
    """
    Obtiene información básica de un archivo.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Información del archivo (tamaño, modificación, etc.)
        
    Raises:
        FileNotFoundError: Si el archivo no existe
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
