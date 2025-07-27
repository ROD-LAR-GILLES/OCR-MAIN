"""
Contenedor de dependencias para FastAPI.
Gestiona la inyección de dependencias siguiendo Clean Architecture.
"""
import logging
import traceback 
from functools import lru_cache
from typing import Annotated

from fastapi import Depends

# Configurar logging
logger = logging.getLogger(__name__)


class DefaultSystemConfig:
    """Configuración por defecto del sistema."""
    
    def __init__(self):
        self.output_directory = "./resultado"
        self.default_language = "spa"
        self.default_dpi = 300
        self.tesseract_config = "--oem 3 --psm 6"
        self.input_directory = "./pdfs"
        self.logs_directory = "./logs"
        #  AGREGAR ATRIBUTOS FALTANTES
        self.engine_type = "basic"
        self.language = "spa"
        self.dpi = 300
        self.confidence_threshold = 60.0
        # Nueva configuración para Markdown
        self.enable_markdown_output = True
        self.markdown_template = "default"


@lru_cache()
def get_system_config() -> DefaultSystemConfig:
    """
    Obtener configuración del sistema.
    
    Returns:
        DefaultSystemConfig: Configuración del sistema
    """
    try:
        # Intentar importar la configuración real
        from infrastructure.config.system_config import SystemConfig
        config = SystemConfig()
        
        # VERIFICAR Y AGREGAR ATRIBUTOS FALTANTES
        if not hasattr(config, 'output_directory'):
            logger.warning("SystemConfig no tiene output_directory, usando configuración por defecto")
            return DefaultSystemConfig()
        
        # Agregar atributos faltantes si no existen
        if not hasattr(config, 'engine_type'):
            config.engine_type = "basic"
        if not hasattr(config, 'language'):
            config.language = getattr(config, 'default_language', 'spa')
        if not hasattr(config, 'dpi'):
            config.dpi = getattr(config, 'default_dpi', 300)
        if not hasattr(config, 'confidence_threshold'):
            config.confidence_threshold = 60.0
        
        logger.info("Configuración del sistema cargada correctamente")
        return config
        
    except ImportError:
        logger.warning("No se pudo importar SystemConfig, usando configuración por defecto")
        return DefaultSystemConfig()
    except Exception as e:
        logger.error(f"Error al cargar configuración del sistema: {e}")
        logger.info("Usando configuración por defecto")
        return DefaultSystemConfig()


@lru_cache()
def get_markdown_generator():
    """
    Obtener generador de Markdown.
    
    Returns:
        MarkdownGenerator: Instancia del generador
    """
    try:
        from domain.services.markdown_generator import MarkdownGenerator
        generator = MarkdownGenerator()
        logger.info("Generador de Markdown creado correctamente")
        return generator
    except ImportError:
        logger.warning("No se pudo importar MarkdownGenerator, usando mock")
        return MockMarkdownGenerator()
    except Exception as e:
        logger.error(f"Error al crear generador de Markdown: {e}")
        return MockMarkdownGenerator()


class MockMarkdownGenerator:
    """Generador mock de Markdown para testing."""
    
    def generate_markdown(self, extracted_text: str, document_metadata: dict, tables=None, output_path=None) -> str:
        """Generar Markdown mock."""
        filename = document_metadata.get('filename', 'documento.pdf')
        return f"""# {filename}

## Contenido Extraído (Mock)

{extracted_text[:500] if extracted_text else 'No hay texto disponible'}...

*Generado por MockMarkdownGenerator*
"""
    
    def generate_summary_markdown(self, documents: list, output_path=None) -> str:
        """Generar resumen mock."""
        return f"""# Resumen Mock

Total de documentos: {len(documents)}

*Generado por MockMarkdownGenerator*
"""


class MockDocumentProcessor:
    """Procesador mock para cuando no esté disponible el real."""
    
    def execute(self, file_path=None, pdf_path=None, filename=None, engine_type="mock", 
                language="spa", dpi=300, extract_tables=True, **kwargs):
        """Ejecutar procesamiento mock con interfaz completa."""
        from datetime import datetime
        import uuid
        from pathlib import Path
        
        # Usar file_path si está disponible, sino pdf_path
        source_path = file_path or pdf_path
        if isinstance(source_path, str):
            source_path = Path(source_path)
        
        # Generar ID único
        document_id = str(uuid.uuid4())[:8]
        
        # Crear directorio de salida
        output_dir = Path('./resultado')
        output_dir.mkdir(exist_ok=True)
        
        # Extraer texto mock basado en el filename
        if filename:
            base_text = f"Contenido extraído del archivo: {filename}"
        else:
            base_text = f"Contenido extraído del archivo: {source_path.name}"
        
        mock_text = f"""
{base_text}

Este es un texto de ejemplo generado por el procesador mock.
El documento fue procesado con los siguientes parámetros:
- Motor: {engine_type}
- Idioma: {language}
- DPI: {dpi}
- Extraer tablas: {extract_tables}

El procesamiento se completó exitosamente.
        """.strip()
        
        # Crear resultado mock
        class MockResult:
            def __init__(self):
                self.document_id = document_id
                self.extracted_text = mock_text
                self.tables = []
                self.confidence_score = 95.0
                self.processing_time = 1.5
                self.output_directory = output_dir
                self.total_pages = 1
                self.generated_files = []
        
        result = MockResult()
        
        logger.info(f"Procesamiento mock completado para {filename or source_path}")
        return result


def get_document_processor(
    config: Annotated[DefaultSystemConfig, Depends(get_system_config)]
):
    """
    Crear procesador de documentos real (no mock).
    """
    try:
        from pathlib import Path
        from infrastructure.factories.adapter_factory import AdapterFactory
        from application.use_cases.process_document import ProcessDocument
        
        logger.info(" Creando procesador REAL de documentos...")
        
        # Crear directorios necesarios
        output_dir = Path(config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # VERIFICAR QUE CONFIG TENGA TODOS LOS ATRIBUTOS
        logger.info(f"Config engine_type: {getattr(config, 'engine_type', 'basic')}")
        logger.info(f"Config language: {getattr(config, 'language', 'spa')}")
        logger.info(f"Config dpi: {getattr(config, 'dpi', 300)}")
        
        # Crear adaptadores reales
        ocr_adapter = AdapterFactory.create_ocr_adapter(config)
        table_adapter = AdapterFactory.create_table_extractor()
        storage_adapter = AdapterFactory.create_storage_adapter(output_dir)
        
        # USAR PROCESADOR REAL
        processor = ProcessDocument(
            ocr=ocr_adapter,
            table_extractor=table_adapter,
            storage=storage_adapter
        )
        
        logger.info(" Procesador REAL creado correctamente")
        return processor
        
    except Exception as e:
        logger.error(f" Error creando procesador real: {e}")
        logger.error(f" Traceback: {traceback.format_exc()}")  
        
        # Solo como último recurso usar mock
        logger.warning(" Usando procesador MOCK como fallback")
        return MockDocumentProcessor()


# Aliases para facilitar el uso
SystemConfigDep = Annotated[DefaultSystemConfig, Depends(get_system_config)]
DocumentProcessorDep = Annotated[object, Depends(get_document_processor)]
MarkdownGeneratorDep = Annotated[object, Depends(get_markdown_generator)]

from infrastructure.services.file_manager import PersistentFileManager

def get_file_manager() -> PersistentFileManager:
    """Obtener gestor de archivos persistente."""
    return PersistentFileManager(storage_dir="pdfs", metadata_file="files_metadata.json")

FileManagerDep = Annotated[PersistentFileManager, Depends(get_file_manager)]