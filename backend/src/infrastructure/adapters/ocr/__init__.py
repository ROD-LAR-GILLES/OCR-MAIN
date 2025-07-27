"""
Adaptadores OCR.
"""
from .tesseract_adapter import TesseractAdapter
from .tesseract_opencv_adapter import TesseractOpenCVAdapter

__all__ = ['TesseractAdapter', 'TesseractOpenCVAdapter']