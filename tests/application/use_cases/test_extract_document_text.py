import unittest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from domain.ports import OCRPort
from application.use_cases.extract_document_text import ExtractDocumentTextUseCase

class TestExtractDocumentTextUseCase(unittest.TestCase):
    
    def setUp(self):
        # Crear mock de OCRPort
        self.ocr_mock = Mock(spec=OCRPort)
        self.ocr_mock.extract_text.return_value = "Texto extraído de prueba"
        self.ocr_mock.get_confidence.return_value = 95.5
        
        # Crear caso de uso con el mock
        self.use_case = ExtractDocumentTextUseCase(self.ocr_mock)
        
        # Ruta de prueba
        self.test_pdf = Path("/tmp/test.pdf")
    
    def test_execute_returns_text_and_confidence(self):
        # Ejecutar caso de uso
        text, confidence = self.use_case.execute(self.test_pdf)
        
        # Verificar resultado
        self.assertEqual(text, "Texto extraído de prueba")
        self.assertEqual(confidence, 95.5)
        
        # Verificar que se llamó al adaptador correctamente
        self.ocr_mock.extract_text.assert_called_once_with(self.test_pdf)
        self.ocr_mock.get_confidence.assert_called_once()