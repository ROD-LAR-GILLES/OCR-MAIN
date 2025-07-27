# adapters/table_pdfplumber.py
"""
Extracción de tablas con pdfplumber.
"""
from pathlib import Path
from typing import List

import pdfplumber
import pandas as pd

from application.ports import TableExtractorPort


class PdfPlumberAdapter(TableExtractorPort):
    """Extrae tablas de PDFs nativos usando pdfplumber."""

    def extract_tables(self, pdf_path: Path) -> List[pd.DataFrame]:
        """
        Extrae todas las tablas detectadas en un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de DataFrames con las tablas encontradas
        """
        dfs: List[pd.DataFrame] = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                for table in page.extract_tables():
                    df = pd.DataFrame(table)
                    if self._is_valid_table(df):
                        dfs.append(df)
                    
        return dfs
    
    def _is_valid_table(self, df: pd.DataFrame) -> bool:
        """Valida si una tabla extraída es significativa."""
        # Filtro 1: Tamaño mínimo - necesitamos al menos 2x2 para una tabla real
        if df.shape[0] < 2 or df.shape[1] < 2:
            return False
        
        # Filtro 2: Demasiadas celdas vacías
        total_cells = df.shape[0] * df.shape[1]
        empty_cells = df.isnull().sum().sum() + (df == '').sum().sum()
        if empty_cells / total_cells > 0.6:  # Más del 60% vacío
            return False
            
        # Filtro 3: Tabla demasiado pequeña (menos de 8 celdas total)
        if total_cells < 8:
            return False
            
        # Filtro 4: Detectar tablas que son solo listas numeradas (como la problemática)
        if df.shape[1] == 2:  # Exactamente dos columnas
            try:
                first_col = df.iloc[:, 0].astype(str).str.strip()
                second_col = df.iloc[:, 1].astype(str).str.strip()
                
                # Verificar si la primera columna son números consecutivos empezando en 0
                if len(first_col) >= 3:  # Al menos 3 filas
                    try:
                        nums = [int(x) for x in first_col if x.isdigit()]
                        if len(nums) == len(first_col) and nums == list(range(len(nums))):
                            # Es una secuencia 0,1,2,3... - probablemente un índice, no una tabla real
                            return False
                    except (ValueError, TypeError):
                        pass
                
                # Verificar si contiene palabras clave que indican que es un índice de contenido
                content_keywords = ['cabecera', 'cuerpo', 'tabla', 'trailer', 'índice', 'contenido']
                second_col_text = ' '.join(second_col).lower()
                keyword_matches = sum(1 for keyword in content_keywords if keyword in second_col_text)
                if keyword_matches >= 2:  # Si aparecen 2 o más palabras clave, es probablemente un índice
                    return False
                    
            except Exception:
                pass
        
        # Filtro 5: Contenido muy repetitivo o vacío
        unique_values = set()
        for col in df.columns:
            col_values = df[col].dropna().astype(str).str.strip()
            col_values = col_values[col_values != '']  # Remover strings vacíos
            unique_values.update(col_values.unique())
        
        # Si hay muy pocos valores únicos no vacíos
        if len(unique_values) < 3:
            return False
            
        # Filtro 6: Verificar que haya contenido sustantivo
        # Al menos el 50% de las celdas deben tener contenido no trivial
        non_trivial_content = 0
        for col in df.columns:
            for val in df[col]:
                if val is not None and str(val).strip() and len(str(val).strip()) > 1:
                    non_trivial_content += 1
        
        if non_trivial_content / total_cells < 0.5:
            return False
            
        return True