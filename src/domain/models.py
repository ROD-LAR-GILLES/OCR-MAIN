"""
Modelos del dominio.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Document:
    """Modelo de documento procesado."""
    # Argumentos requeridos (sin valores por defecto)
    name: str
    path: Path
    extracted_text: str
    tables: List[Dict[str, Any]]
    confidence: float
    # Argumentos opcionales (con valores por defecto)
    output_directory: Optional[Path] = None
    generated_files: Optional[List[Path]] = None
    
    def __str__(self) -> str:
        return f"Document(name='{self.name}', confidence={self.confidence:.1f}%)"
    
    def __repr__(self) -> str:
        return (f"Document(name='{self.name}', "
                f"confidence={self.confidence:.1f}%, "
                f"tables={len(self.tables)}, "
                f"text_length={len(self.extracted_text)})")