import unittest
from pathlib import Path
import tempfile
import os

from domain.ports import OCRPort
from adapters.ocr.tesseract_adapter import TesseractAdapter
from infrastructure.config.system_config import SystemConfig


class TestOCRAdapters(unittest.TestCase):
    
    def setUp(self):
        self.config = SystemConfig(language="eng", dpi=300)
        self.test_pdf = Path("tests/fixtures/sample.pdf")
        
        # Crear PDF de prueba si no existe
        if not self.test_pdf.exists():
            os.makedirs(self.test_pdf.parent, exist_ok=True)
            with open(self.test_pdf, "wb") as f:
                f.write(b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 22 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000120 00000 n\n0000000210 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n280\n%%EOF")
    
    def test_adapter_implements_port(self):
        """Verificar que los adaptadores implementan los puertos correctamente."""
        adapter = TesseractAdapter.from_config(self.config)
        self.assertIsInstance(adapter, OCRPort)
        
        # Verificar métodos requeridos
        self.assertTrue(hasattr(adapter, "extract_text"))
        self.assertTrue(hasattr(adapter, "get_engine_info"))
        self.assertTrue(hasattr(adapter, "get_supported_languages"))
    
    def test_extract_text(self):
        """Verificar que extract_text funciona."""
        adapter = TesseractAdapter.from_config(self.config)
        try:
            text = adapter.extract_text(self.test_pdf)
            # Solo verificar que devuelva algo sin error
            self.assertIsInstance(text, str)
        except Exception as e:
            self.fail(f"extract_text lanzó excepción: {e}")