"""
Adaptador de Tesseract con preprocesamiento OpenCV.
"""
from pathlib import Path
import logging
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path

from application.ports import OCRPort
from domain.exceptions import ProcessingError
from infrastructure.config.system_config import SystemConfig

logger = logging.getLogger(__name__)


class TesseractOpenCVAdapter(OCRPort):
    """Adaptador OCR con preprocesamiento OpenCV."""

    def __init__(self, lang: str = "spa", dpi: int = 300) -> None:
        self.lang = lang
        self.dpi = dpi
        self.last_confidence = 0.0
        logger.info(f"TesseractOpenCVAdapter inicializado: lang={lang}, dpi={dpi}")

    @classmethod
    def from_config(cls, config: SystemConfig) -> 'TesseractOpenCVAdapter':
        """Crea adaptador desde configuración."""
        return cls(lang=config.language, dpi=config.dpi)

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocesa imagen con OpenCV."""
        # Convertir a escala de grises
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Aplicar threshold adaptativo
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducir ruido
        denoised = cv2.medianBlur(binary, 3)
        
        return denoised

    def extract_text(self, pdf_path: Path) -> str:
        """Extrae texto usando OCR con preprocesamiento."""
        try:
            logger.info(f"Iniciando extracción con OpenCV de: {pdf_path}")
            
            images = convert_from_path(pdf_path, dpi=self.dpi)
            extracted_text = []
            
            for page_num, image in enumerate(images, 1):
                logger.debug(f"Procesando página {page_num}/{len(images)} con OpenCV")
                
                # Preprocesar imagen
                processed_image = self._preprocess_image(image)
                
                # Extraer texto
                text = pytesseract.image_to_string(processed_image, lang=self.lang)
                extracted_text.append(text)
            
            final_text = "\n\n".join(extracted_text)
            logger.info(f"Extracción con OpenCV completada. Páginas: {len(images)}")
            
            return final_text
            
        except Exception as e:
            raise ProcessingError(f"Error en OCR con OpenCV: {str(e)}")

    def get_confidence(self) -> float:
        """Retorna el nivel de confianza de la última extracción."""
        return self.last_confidence