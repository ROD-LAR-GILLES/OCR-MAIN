"""
Adaptador básico de Tesseract.
"""
from pathlib import Path
import logging
import pytesseract
from pdf2image import convert_from_path

from application.ports import OCRPort
from domain.exceptions import ProcessingError
from infrastructure.config.system_config import SystemConfig

logger = logging.getLogger(__name__)


class TesseractAdapter(OCRPort):
    """Adaptador básico de OCR usando Tesseract."""

    def __init__(self, lang: str = "spa", dpi: int = 300) -> None:
        self.lang = lang
        self.dpi = dpi
        self.last_confidence = 0.0
        logger.info(f"TesseractAdapter inicializado: lang={lang}, dpi={dpi}")

    @classmethod
    def from_config(cls, config: SystemConfig) -> 'TesseractAdapter':
        """Crea adaptador desde configuración."""
        return cls(lang=config.language, dpi=config.dpi)

    def extract_text(self, pdf_path: Path) -> str:
        """Extrae texto usando OCR básico sin OpenCV."""
        try:
            logger.info(f"Iniciando extracción básica de: {pdf_path}")
            
            # Convertir PDF a imágenes
            images = convert_from_path(pdf_path, dpi=self.dpi)
            extracted_text = []
            
            for page_num, image in enumerate(images, 1):
                logger.debug(f"Procesando página {page_num}/{len(images)}")
                
                # Extraer texto directamente sin preprocesamiento OpenCV
                text = pytesseract.image_to_string(image, lang=self.lang)
                extracted_text.append(text)
            
            final_text = "\n\n".join(extracted_text)
            logger.info(f"Extracción completada. Páginas: {len(images)}")
            
            return final_text
            
        except Exception as e:
            logger.error(f"Error en OCR básico: {str(e)}")
            raise ProcessingError(f"Error en OCR básico: {str(e)}")

    def get_confidence(self) -> float:
        """Retorna el nivel de confianza de la última extracción."""
        return self.last_confidence