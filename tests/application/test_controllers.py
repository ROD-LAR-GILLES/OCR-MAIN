import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Asegurarnos de que src esté en el PYTHONPATH
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.application.controllers import DocumentController
from src.domain.exceptions import OCRError, ProcessingError
from src.domain.entities.document import Document


class TestDocumentController(unittest.TestCase):
    
    def setUp(self):
        # Crear mock del caso de uso ProcessDocument
        self.process_document_mock = Mock()
        
        # Mock de extract_text
        self.extract_text_mock = Mock()
        self.extract_text_mock.execute.return_value = ("Texto de prueba", 95.0)
        
        # Mock de extract_tables
        self.extract_tables_mock = Mock()
        self.extract_tables_mock.execute.return_value = []
        
        # Crear controlador con los mocks
        self.controller = DocumentController(
            self.process_document_mock,
            self.extract_text_mock,
            self.extract_tables_mock
        )
        
        # Crear documento de prueba
        self.test_document = Document(
            name="test_doc",
            text="Texto de prueba",
            tables=[]
        )
        self.test_document.confidence = 95.0
        self.test_document.output_directory = Path("/tmp/test")
        self.test_document.processing_time = 1.5
        
        # Configurar mock para retornar el documento
        self.process_document_mock.return_value = self.test_document
        self.process_document_mock.__call__ = self.process_document_mock
    
    def test_process_pdf_success(self):
        """Prueba el procesamiento exitoso de un PDF."""
        # Ejecutar controlador
        result = self.controller.process_pdf(Path("/tmp/test.pdf"))
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertEqual(result["document"], "test_doc")
        self.assertEqual(result["text_length"], len("Texto de prueba"))
        self.assertEqual(result["tables_count"], 0)
        self.assertEqual(result["output_dir"], "/tmp/test")
        self.assertEqual(result["confidence"], 95.0)
        self.assertEqual(result["processing_time"], 1.5)
        
        # Verificar que se llamó al caso de uso
        self.process_document_mock.assert_called_once_with(Path("/tmp/test.pdf"))
    
    def test_process_pdf_domain_error(self):
        """Prueba el manejo de errores de dominio."""
        # Configurar mock para lanzar error
        self.process_document_mock.side_effect = OCRError("Error en OCR")
        
        # Ejecutar controlador
        result = self.controller.process_pdf(Path("/tmp/test.pdf"))
        
        # Verificar resultado
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Error en OCR")
        self.assertTrue("Error" in result["message"])
    
    def test_extract_document_text(self):
        """Prueba la extracción de texto."""
        # Ejecutar controlador
        result = self.controller.extract_document_text(Path("/tmp/test.pdf"))
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertEqual(result["text"], "Texto de prueba")
        self.assertEqual(result["text_length"], len("Texto de prueba"))
        self.assertEqual(result["confidence"], 95.0)
        
        # Verificar que se llamó al caso de uso
        self.extract_text_mock.execute.assert_called_once_with(Path("/tmp/test.pdf"))
    
    def test_extract_document_tables(self):
        """Prueba la extracción de tablas."""
        # Ejecutar controlador
        result = self.controller.extract_document_tables(Path("/tmp/test.pdf"))
        
        # Verificar resultado
        self.assertTrue(result["success"])
        self.assertEqual(result["tables"], [])
        self.assertEqual(result["tables_count"], 0)
        
        # Verificar que se llamó al caso de uso
        self.extract_tables_mock.execute.assert_called_once_with(Path("/tmp/test.pdf"))


if __name__ == "__main__":
    unittest.main()