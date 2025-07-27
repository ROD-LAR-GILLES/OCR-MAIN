import unittest
import tempfile
import shutil
from pathlib import Path

from domain.ports import OCRPort, TableExtractorPort, StoragePort
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.config.system_config import SystemConfig
from application.use_cases.process_document import ProcessDocument

class TestDocumentProcessingIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Crear un PDF simple para pruebas
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.test_pdf = cls.test_dir / "test_doc.pdf"
        
        # Escribir un PDF mínimo válido
        with open(cls.test_pdf, "wb") as f:
            f.write(b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 22 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000120 00000 n\n0000000210 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n280\n%%EOF")
    
    @classmethod
    def tearDownClass(cls):
        # Limpiar archivos temporales
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        # Crear configuración
        self.config = SystemConfig(language="eng", dpi=300, engine_type="basic")
        
        # Crear adaptadores reales
        self.ocr = AdapterFactory.create_ocr_adapter(self.config)
        self.table_extractor = AdapterFactory.create_table_extractor()
        
        # Crear directorio para resultados
        self.output_dir = self.test_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.storage = AdapterFactory.create_storage_adapter(self.output_dir)
        
        # Crear caso de uso principal
        self.process_document = ProcessDocument(
            ocr=self.ocr,
            table_extractor=self.table_extractor,
            storage=self.storage
        )
    
    def test_full_document_processing(self):
        # Ejecutar procesamiento completo
        document = self.process_document.execute(self.test_pdf)
        
        # Verificar resultado
        self.assertIsNotNone(document)
        self.assertTrue(len(document.extracted_text) > 0)
        
        # Verificar archivos generados
        self.assertTrue(len(document.generated_files) > 0)
        for file_path in document.generated_files:
            self.assertTrue(file_path.exists())