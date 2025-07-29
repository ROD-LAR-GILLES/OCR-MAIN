# interfaces/cli/menu.py
"""
Interfaz de línea de comandos para el sistema OCR.
"""
import argparse
import logging
from pathlib import Path

from application.use_cases import ProcessDocument
from infrastructure.config.system_config import SystemConfig
# Corregir import
from infrastructure.factories.adapter_factory import AdapterFactory
from domain.exceptions import DomainError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Punto de entrada principal de la CLI."""
    parser = argparse.ArgumentParser(description="Sistema OCR para procesamiento de PDFs")
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
    
    args = parser.parse_args()

    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger.info("Iniciando sistema OCR...")
        
        # Crear configuración
        config = SystemConfig(
            engine_type=args.engine,
            output_dir=args.output_dir
        )
        
        # Crear adaptadores usando el factory
        factory = AdapterFactory()
        ocr = factory.create_ocr_adapter(config)
        table_extractor = factory.create_table_extractor()
        storage = factory.create_storage_adapter(config.output_dir)
        
        logger.info(f"Adaptadores creados: engine={config.engine_type}")
        
        # Crear caso de uso
        process_doc = ProcessDocument(ocr, table_extractor, storage)
        
        # Ejecutar procesamiento
        logger.info(f"Procesando: {args.pdf_path}")
        document = process_doc.execute(args.pdf_path)
        
        print(f"\n Proceso completado exitosamente!")
        print(f" Documento: {document.name}")
        print(f" Texto extraído: {len(document.extracted_text)} caracteres")
        print(f" Tablas encontradas: {len(document.tables)}")
        print(f" Resultados guardados en: {config.output_dir}")
        
        return 0
        
    except DomainError as e:
        logger.error(f"Error del dominio: {str(e)}")
        print(f" Error: {str(e)}")
        return 1
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {str(e)}")
        print(f" Archivo no encontrado: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        print(f" Error inesperado: {str(e)}")
        return 2


if __name__ == "__main__":
    exit(main())
