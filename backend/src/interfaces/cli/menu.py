# interfaces/cli/menu.py
"""
Interfaz de línea de comandos para el sistema OCR.
"""
import argparse
import logging
import sys
from pathlib import Path

# Asegurarnos de que src esté en el PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.domain.exceptions import OCRError, ProcessingError
from src.application.controllers import DocumentController
from src.infrastructure.config.system_config import SystemConfig
from src.infrastructure.factories.adapter_factory import AdapterFactory
from src.application.use_cases.process_document import ProcessDocument

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Sistema OCR para procesamiento de documentos PDF"
    )
    
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Ruta al archivo PDF a procesar"
    )
    
    parser.add_argument(
        "--engine",
        choices=["basic", "opencv"],
        default="basic",
        help="Motor OCR a utilizar (default: basic)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("resultado"),
        help="Directorio de salida (default: resultado)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Activar logging detallado"
    )
    
    parser.add_argument(
        "--mode",
        choices=["full", "text", "tables"],
        default="full",
        help="Modo de procesamiento (default: full)"
    )
    
    return parser.parse_args()


def main():
    """Punto de entrada principal del CLI."""
    args = parse_arguments()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Validar archivo PDF
        if not args.pdf_path.exists():
            raise FileNotFoundError(f"El archivo {args.pdf_path} no existe")
        
        if not args.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"El archivo debe ser un PDF")
        
        # Crear configuración
        config = SystemConfig()
        config.engine_type = args.engine
        output_dir = args.output_dir
        
        logger.info(f"Configuración: engine={config.engine_type}, output_dir={output_dir}")
        
        # Crear adaptadores usando factory
        factory = AdapterFactory()
        ocr = factory.create_ocr_adapter(config)
        table_extractor = factory.create_table_extractor()
        storage = factory.create_storage_adapter(output_dir)
        
        logger.info(f"Adaptadores creados: engine={config.engine_type}")
        
        # Crear caso de uso principal
        process_doc = ProcessDocument(ocr, table_extractor, storage)
        
        # Crear controlador con el caso de uso
        controller = DocumentController(process_doc)
        
        # Determinar la operación según el modo
        if args.mode == "text":
            result = controller.extract_document_text(args.pdf_path)
        elif args.mode == "tables":
            result = controller.extract_document_tables(args.pdf_path)
        else:  # mode == "full"
            result = controller.process_pdf(args.pdf_path)
        
        # Mostrar resultados
        if result["success"]:
            print(f"\n{result['message']}")
            
            if args.mode == "full":
                print(f"Documento: {result['document']}")
                print(f"Texto extraído: {result['text_length']} caracteres")
                print(f"Tablas encontradas: {result['tables_count']}")
                print(f"Resultados guardados en: {result['output_dir']}")
            elif args.mode == "text":
                print(f"Texto extraído: {result['text_length']} caracteres")
                print(f"Confianza OCR: {result['confidence']}%")
            elif args.mode == "tables":
                print(f"Tablas encontradas: {result['tables_count']}")
        else:
            print(f"\n{result['message']}")
        
        return 0 if result["success"] else 1
        
    except (OCRError, ProcessingError) as e:
        logger.error(f"Error del dominio: {str(e)}")
        print(f"Error: {str(e)}")
        return 1
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {str(e)}")
        print(f"Archivo no encontrado: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        print(f"Error inesperado: {str(e)}")
        return 2


if __name__ == "__main__":
    exit(main())
