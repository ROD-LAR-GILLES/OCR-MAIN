# interfaces/cli/menu.py
"""
Interfaz simplificada de línea de comandos para OCR-CLI.
"""

from pathlib import Path
from typing import List, Optional
import logging

from utils.file_utils import discover_pdf_files, validate_pdf_exists, ensure_directory_exists
from utils.menu_logic import (
    create_pdf_menu_options, 
    get_selected_pdf, 
    is_exit_selection,
    detect_pdf_type_automatically,
    validate_menu_selection
)
from config.system_config import SystemConfig
from application.controllers import DocumentController
from shared.constants import DEFAULT_PDF_DIR, DEFAULT_OUTPUT_DIR
from shared.exceptions import DocumentNotFoundError, ProcessingError

logger = logging.getLogger(__name__)


def display_welcome_message() -> None:
    """
    Muestra mensaje de bienvenida del sistema.
    """
    print("=" * 50)
    print("OCR-CLI - Procesador inteligente de PDFs")
    print("=" * 50)
    print("Detección automática activada")
    print("Procesamiento optimizado por tipo de documento")


def display_pdf_menu(pdf_files: List[str]) -> None:
    """
    Muestra menú de selección de archivos PDF.
    
    Args:
        pdf_files: Lista de nombres de archivos PDF
    """
    print("Selecciona un PDF para procesar:")
    
    menu_options = create_pdf_menu_options(pdf_files)
    
    for option in menu_options:
        print(option.text)
    
    print("-" * 50)



def get_user_pdf_selection(total_options: int) -> int:
    """
    Captura y valida selección de PDF del usuario.
    """
    from utils.menu_logic import validate_menu_selection
    
    while True:
        try:
            choice = int(input("Ingresa tu opción: "))
            if validate_menu_selection(choice, total_options):
                return choice
            else:
                print(f"Selección inválida. Ingresa un número entre 1 y {total_options}.")
        except ValueError:
            print("Entrada inválida. Ingresa un número.")
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            return total_options  # Retorna la opción de salida


def display_processing_success(processing_info: dict) -> None:
    """
    Muestra información de procesamiento exitoso.
    """
    print(f"\n{processing_info['filename']} procesado exitosamente!")
    print(f"Tiempo: {processing_info['processing_time']:.2f} segundos")
    
    if 'output_files' in processing_info and processing_info['output_files']:
        print(f"Archivos generados:")
        for file_path in processing_info['output_files']:
            print(f"   • {Path(file_path).name}")
    
    # Mostrar información del documento si está disponible
    if 'document_info' in processing_info:
        doc_info = processing_info['document_info']
        if 'files_count' in doc_info:
            print(f"Estadísticas:")
            print(f"   • Total de archivos: {doc_info['files_count']}")


def display_no_pdfs_message() -> None:
    """
    Muestra mensaje cuando no hay PDFs disponibles.
    """
    print("No hay PDFs disponibles en el directorio /pdfs")
    print("Añade archivos PDF al directorio y reconstruye la imagen.")
    logger.warning("No se encontraron PDFs en el directorio")


def display_exit_message() -> None:
    """
    Muestra mensaje de salida de la aplicación.
    """
    print("Saliendo de la aplicación.")
    logger.info("Aplicación finalizada por el usuario")


def process_document_workflow(filename: str) -> None:
    """
    Procesa un documento PDF automáticamente con detección inteligente.
    
    Args:
        filename: Nombre del archivo PDF a procesar
    """
    try:
        print(f"\nProcesando: {filename}")
        logger.info(f"Iniciando procesamiento de {filename}")
        
        # DETECCIÓN AUTOMÁTICA Y CONFIGURACIÓN
        pdf_path = Path(DEFAULT_PDF_DIR) / filename
        
        # Detectar tipo y configuración automáticamente
        config, description = detect_pdf_type_automatically(pdf_path)
        
        print(f"Tipo detectado: {description}")
        print(f"Motor: {config.engine_type.upper()}")
        
        if config.enable_deskewing or config.enable_denoising or config.enable_contrast_enhancement:
            features = []
            if config.enable_deskewing:
                features.append("corrección de inclinación")
            if config.enable_denoising:
                features.append("eliminación de ruido")
            if config.enable_contrast_enhancement:
                features.append("mejora de contraste")
            print(f"Preprocesamiento: {', '.join(features)}")
        
        print("Iniciando procesamiento...")
        
        # CONFIGURAR DIRECTORIOS
        pdf_directory = Path(DEFAULT_PDF_DIR)
        output_directory = Path(DEFAULT_OUTPUT_DIR)
        
        # Asegurar que los directorios existen
        ensure_directory_exists(pdf_directory)
        ensure_directory_exists(output_directory)
        
        # PROCESAMIENTO
        controller = DocumentController(pdf_directory, output_directory)
        success, result = controller.process_document(filename, config)
        
        if success:
            display_processing_success({
                'filename': filename,
                'processing_time': result.get('processing_time', 0),
                'output_files': result.get('generated_files', []),
                'document_info': {
                    'files_count': result.get('files_count', 0)
                },
                'config_used': config
            })
            logger.info(f"Procesamiento exitoso de {filename}")
        else:
            error_msg = result.get('error', 'Error desconocido')
            print(f"\nError procesando {filename}: {error_msg}")
            logger.error(f"Error procesando {filename}: {error_msg}")
            
    except DocumentNotFoundError as e:
        print(f"\nArchivo no encontrado: {e}")
        logger.error(f"Archivo no encontrado: {e}")
    except ProcessingError as e:
        print(f"\nError de procesamiento: {e}")
        logger.error(f"Error de procesamiento: {e}")
    except Exception as e:
        print(f"\nError inesperado procesando {filename}: {str(e)}")
        print("Sugerencia: Verifica que el archivo no esté corrupto o protegido")
        logger.exception(f"Error inesperado procesando {filename}")


def main() -> None:
    """
    Función principal del CLI simplificado.
    Muestra PDFs disponibles y procesa automáticamente.
    """
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Iniciando aplicación OCR-CLI")
    
    while True:
        try:
            # PASO 1: MOSTRAR BIENVENIDA
            display_welcome_message()
            
            # PASO 2: DESCUBRIR PDFs
            pdf_directory = Path(DEFAULT_PDF_DIR)
            
            try:
                pdf_files = discover_pdf_files(pdf_directory)
            except DocumentNotFoundError:
                display_no_pdfs_message()
                break
            
            if not pdf_files:
                display_no_pdfs_message()
                break
            
            # PASO 3: MOSTRAR MENÚ DE PDFs
            display_pdf_menu(pdf_files)
            
            # PASO 4: OBTENER SELECCIÓN
            total_options = len(pdf_files) + 1  # +1 para la opción "Salir"
            user_choice = get_user_pdf_selection(total_options)
            
            # PASO 5: PROCESAR SELECCIÓN
            if is_exit_selection(user_choice, len(pdf_files)):
                display_exit_message()
                break
            
            try:
                selected_pdf = get_selected_pdf(pdf_files, user_choice)
                
                # Validar que el archivo aún existe
                if not validate_pdf_exists(pdf_directory, selected_pdf):
                    print(f"Error: {selected_pdf} no existe o no es accesible.")
                    logger.error(f"PDF no accesible: {selected_pdf}")
                    continue
                
                # PASO 6: PROCESAMIENTO AUTOMÁTICO
                process_document_workflow(selected_pdf)
                
                # Preguntar si continuar
                continue_choice = input("\n¿Procesar otro documento? (s/n): ").lower()
                if not continue_choice.startswith('s'):
                    display_exit_message()
                    break
                    
            except (ValueError, IndexError) as e:
                print(f"Error en la selección: {e}")
                logger.error(f"Error en selección: {e}")
                continue
                
        except KeyboardInterrupt:
            print("\nSalida solicitada por el usuario.")
            logger.info("Salida por KeyboardInterrupt")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")
            print("Contacta al administrador del sistema.")
            logger.exception("Error inesperado en main()")
            break


if __name__ == "__main__":
    """
    Punto de entrada directo del módulo.
    """
    main()
