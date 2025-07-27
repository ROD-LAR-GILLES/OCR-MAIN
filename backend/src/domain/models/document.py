"""
Entidad Document del dominio.
"""
from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class Document:
    """Entidad de documento en el dominio."""
    name: str
    source_path: str
    extracted_text: str = ""
    tables: List[Any] = field(default_factory=list)
    
    def add_text(self, text: str) -> None:
        """Añade texto al documento."""
        if self.extracted_text:
            self.extracted_text += "\n\n" + text
        else:
            self.extracted_text = text
    
    def add_table(self, table: Any) -> None:
        """Añade una tabla al documento."""
        self.tables.append(table)