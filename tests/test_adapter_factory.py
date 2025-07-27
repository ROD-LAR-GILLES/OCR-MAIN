import unittest
from pathlib import Path

from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.config.system_config import SystemConfig
from domain.ports import OCRPort, TableExtractorPort, StoragePort


class TestAdapterFactory(unittest.TestCase):
    
    def setUp(self):
        self.config = SystemConfig(language="eng", dpi=300)
        self.output_dir = Path("/tmp/ocr_test")
    
    def test_create_ocr_adapter(self):
        """Verificar creación de adaptador OCR."""
        adapter = AdapterFactory.create_ocr_adapter(self.config)
        self.assertIsInstance(adapter, OCRPort)
    
    def test_create_table_extractor(self):
        """Verificar creación de extractor de tablas."""
        adapter = AdapterFactory.create_table_extractor()
        self.assertIsInstance(adapter, TableExtractorPort)
    
    def test_create_storage_adapter(self):
        """Verificar creación de adaptador de almacenamiento."""
        adapter = AdapterFactory.create_storage_adapter(self.output_dir)
        self.assertIsInstance(adapter, StoragePort)