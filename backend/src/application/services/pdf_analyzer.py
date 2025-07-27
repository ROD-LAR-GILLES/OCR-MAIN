# utils/pdf_analyzer.py
"""
Análisis automático de PDFs - Capa de Aplicación.
"""
from pathlib import Path
from typing import Dict, Any, Tuple
from enum import Enum
import logging

# Actualizar imports para nueva arquitectura
from infrastructure.config.system_config import SystemConfig
from domain.constants import ENGINE_TYPE_BASIC, ENGINE_TYPE_OPENCV, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


class PDFType(Enum):
    """Tipos de PDF detectados automáticamente."""
    SCANNED = "scanned"           # Documento escaneado (requiere OCR completo)
    NATIVE_TEXT = "native_text"   # PDF nativo con texto extraíble
    MIXED = "mixed"               # Documento mixto (texto + imágenes)
    TABLE_HEAVY = "table_heavy"   # Formularios o documentos con muchas tablas
    IMAGE_HEAVY = "image_heavy"   # Documento con muchas imágenes


class PDFAnalyzer:
    """
    Analizador automático de características de PDFs.
    """
    
    def analyze_pdf(self, pdf_path: Path) -> Tuple[PDFType, Dict[str, Any]]:
        """
        Analiza un PDF y determina el tipo y estrategia óptima.
        
        """
        metrics = self._extract_pdf_metrics(pdf_path)
        pdf_type = self._classify_pdf_type(metrics)
        
        return pdf_type, metrics
    
    def _extract_pdf_metrics(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extrae métricas del PDF para clasificación.
        """

        metrics = {
            'total_pages': 0,
            'text_extractable_pages': 0,
            'total_text_length': 0,
            'total_images': 0,
            'total_tables': 0,
            'avg_text_per_page': 0,
            'has_fonts': False,
            'image_to_page_ratio': 0,
            'table_to_page_ratio': 0
        }
        
        # Análisis con pdfplumber (texto y tablas)
        with pdfplumber.open(pdf_path) as pdf:
            metrics['total_pages'] = len(pdf.pages)
            
            for page in pdf.pages:
                # Texto extraíble
                text = page.extract_text()
                if text and text.strip():
                    metrics['text_extractable_pages'] += 1
                    metrics['total_text_length'] += len(text)
                
                # Tablas detectadas
                tables = page.extract_tables()
                metrics['total_tables'] += len(tables) if tables else 0
        
        # Análisis con PyMuPDF (imágenes y fuentes)
        doc = fitz.open(pdf_path)
        
        for page in doc:
            # Imágenes
            image_list = page.get_images()
            metrics['total_images'] += len(image_list)
            
            # Fuentes (indica texto nativo vs escaneado)
            fonts = page.get_fonts()
            if fonts:
                metrics['has_fonts'] = True
        
        doc.close()
        
        # Cálculos derivados
        if metrics['total_pages'] > 0:
            metrics['avg_text_per_page'] = metrics['total_text_length'] / metrics['total_pages']
            metrics['image_to_page_ratio'] = metrics['total_images'] / metrics['total_pages']
            metrics['table_to_page_ratio'] = metrics['total_tables'] / metrics['total_pages']
        
        return metrics
    
    def _classify_pdf_type(self, metrics: Dict[str, Any]) -> PDFType:
        """
        Clasifica el tipo de PDF basado en las métricas extraídas.
        """
        
        # 1. PDF Escaneado: Pocas fuentes, poco texto extraíble, muchas imágenes
        if (not metrics['has_fonts'] and 
            metrics['text_extractable_pages'] < metrics['total_pages'] * 0.3 and
            metrics['image_to_page_ratio'] > 0.5):
            return PDFType.SCANNED
        
        # 2. Documento con muchas tablas
        if metrics['table_to_page_ratio'] > 0.8:
            return PDFType.TABLE_HEAVY
        
        # 3. Documento con muchas imágenes
        if metrics['image_to_page_ratio'] > 1.5:
            return PDFType.IMAGE_HEAVY
        
        # 4. PDF Nativo: Buena extracción de texto, fuentes presentes
        if (metrics['has_fonts'] and 
            metrics['text_extractable_pages'] > metrics['total_pages'] * 0.8 and
            metrics['avg_text_per_page'] > 100):
            return PDFType.NATIVE_TEXT
        
        # 5. Documento Mixto: Por defecto
        return PDFType.MIXED
    
    def get_optimal_config(self, pdf_type: PDFType) -> Dict[str, Any]:
        """
        Retorna configuración óptima para el tipo de PDF detectado.
        """
        
        configs = {
            PDFType.SCANNED: {
                'engine_type': 'opencv',
                'enable_deskewing': True,
                'enable_denoising': True,
                'enable_contrast_enhancement': True,
                'dpi': 300,
                'strategy': 'full_ocr'
            },
            
            PDFType.NATIVE_TEXT: {
                'engine_type': 'basic',
                'enable_deskewing': False,
                'enable_denoising': False,
                'enable_contrast_enhancement': False,
                'dpi': 150,
                'strategy': 'text_extraction'
            },
            
            PDFType.MIXED: {
                'engine_type': 'opencv',
                'enable_deskewing': True,
                'enable_denoising': False,
                'enable_contrast_enhancement': True,
                'dpi': 250,
                'strategy': 'hybrid'
            },
            
            PDFType.TABLE_HEAVY: {
                'engine_type': 'opencv',
                'enable_deskewing': False,
                'enable_denoising': True,
                'enable_contrast_enhancement': True,
                'dpi': 300,
                'strategy': 'table_focused'
            },
            
            PDFType.IMAGE_HEAVY: {
                'engine_type': 'opencv',
                'enable_deskewing': True,
                'enable_denoising': True,
                'enable_contrast_enhancement': True,
                'dpi': 300,
                'strategy': 'image_focused'
            }
        }
        
        return configs.get(pdf_type, configs[PDFType.MIXED])
