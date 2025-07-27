"""
Menú interactivo para el sistema OCR.
"""
import os
import logging
from pathlib import Path
from typing import Optional, List

from application.use_cases import ProcessDocument
from infrastructure.config.system_config import SystemConfig
from infrastructure.factories.adapter_factory import AdapterFactory
from domain.exceptions import DomainError

# Importar utilidades de menú
from .menu_utils import (
    MenuOption,
    create_pdf_menu_options,
    validate_menu_selection,
    get_selected_pdf,
    is_exit_selection,
    create_ocr_config_from_user_choices,
    detect_pdf_type_automatically,
    validate_ocr_engine_choice
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InteractiveMenu:
    """Menú interactivo para el sistema OCR usando utilidades de menú."""
    
    def __init__(self):
        self.config = SystemConfig()
        self.running = True
        self.pdfs_directory = Path("./pdfs")
        self.results_directory = Path("./resultado")
        logger.info("Menú interactivo inicializado")

    def clear_screen(self):
        """Limpiar pantalla del terminal."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def show_header(self):
        """Mostrar encabezado del sistema."""
        print("=" * 60)
        print("SISTEMA OCR - CLEAN ARCHITECTURE")
        print("=" * 60)
        print()

    def show_main_menu(self):
        """Mostrar menú principal."""
        print("MENU PRINCIPAL")
        print("-" * 30)
        print("1. Procesar documento PDF")
        print("2. Configurar sistema")
        print("3. Ver estado del sistema")
        print("4. Listar archivos disponibles")
        print("5. Ver resultados anteriores")
        print("6. Salir")
        print()

    def get_user_choice(self, max_option: int) -> int:
        """Obtener selección del usuario con validación."""
        while True:
            try:
                choice = int(input(f"Seleccione una opción (1-{max_option}): "))
                if validate_menu_selection(choice, max_option):
                    return choice
                else:
                    print(f"ERROR: Opción inválida. Seleccione entre 1 y {max_option}")
            except ValueError:
                print("ERROR: Por favor ingrese un número válido")
            except KeyboardInterrupt:
                print("\n\nSaliendo del sistema...")
                return max_option  # Opción de salir

    def discover_pdfs(self) -> List[Path]:
        """Descubrir archivos PDF en el directorio."""
        try:
            if not self.pdfs_directory.exists():
                self.pdfs_directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directorio creado: {self.pdfs_directory}")
            
            pdf_files = list(self.pdfs_directory.glob("*.pdf"))
            logger.info(f"PDFs encontrados: {len(pdf_files)}")
            return pdf_files
            
        except Exception as e:
            logger.error(f"Error descubriendo PDFs: {str(e)}")
            return []

    def select_pdf_file(self) -> Optional[Path]:
        """Seleccionar archivo PDF usando utilidades de menú."""
        pdf_files = self.discover_pdfs()
        
        if not pdf_files:
            print("\nERROR: No se encontraron archivos PDF en el directorio ./pdfs/")
            print("NOTA: Coloque archivos PDF en el directorio ./pdfs/ y vuelva a intentar")
            return None
        
        print("\nARCHIVOS PDF DISPONIBLES")
        print("-" * 40)
        
        # Usar utilidades para crear opciones de menú
        file_names = [pdf.name for pdf in pdf_files]
        menu_options = create_pdf_menu_options(file_names)
        
        # Mostrar opciones
        for option in menu_options:
            print(option.text)
        print()
        
        # Obtener selección del usuario
        choice = self.get_user_choice(len(menu_options))
        
        # Verificar si es opción de salir
        if is_exit_selection(choice, len(pdf_files)):
            return None
        
        try:
            # Usar utilidad para obtener archivo seleccionado
            selected_filename = get_selected_pdf(file_names, choice)
            selected_path = self.pdfs_directory / selected_filename
            
            print(f"\nArchivo seleccionado: {selected_filename}")
            return selected_path
            
        except (ValueError, IndexError) as e:
            print(f"ERROR: Error en selección: {str(e)}")
            return None

    def select_ocr_engine(self) -> SystemConfig:
        """Seleccionar motor OCR usando utilidades de menú."""
        print("\nCONFIGURACION DEL MOTOR OCR")
        print("-" * 40)
        print("1. Motor Básico (Tesseract)")
        print("   - Rápido y eficiente")
        print("   - Para documentos con buena calidad")
        print()
        print("2. Motor OpenCV (Avanzado)")
        print("   - Preprocesamiento de imagen")
        print("   - Mejor para documentos escaneados")
        print()
        print("3. Detección Automática")
        print("   - El sistema elige la mejor configuración")
        print()
        
        choice = self.get_user_choice(3)
        
        if choice == 3:
            return None  # Señal para detección automática
        else:
            # Usar utilidad para crear configuración
            try:
                config = create_ocr_config_from_user_choices(choice)
                engine_name = "Básico" if choice == 1 else "OpenCV"
                print(f"Motor seleccionado: {engine_name}")
                return config
            except ValueError as e:
                print(f"ERROR: Error en configuración: {str(e)}")
                return self.config  # Fallback a configuración por defecto

    def process_document(self):
        """Procesar un documento seleccionado usando utilidades de menú."""
        try:
            # 1. Seleccionar PDF
            selected_pdf = self.select_pdf_file()
            if not selected_pdf:
                return
            
            # 2. Seleccionar configuración OCR
            config = self.select_ocr_engine()
            
            if config is None:
                # Detección automática usando utilidad
                print("\nDetectando tipo de documento automáticamente...")
                config, detection_info = detect_pdf_type_automatically(selected_pdf)
                print(f"Resultado: {detection_info}")
            
            print(f"\nConfiguración aplicada:")
            print(f"   Motor: {config.engine_type}")
            print(f"   Idioma: {config.language}")
            print(f"   DPI: {config.dpi}")
            
            # 3. Crear adaptadores usando factory
            factory = AdapterFactory()
            ocr = factory.create_ocr_adapter(config)
            table_extractor = factory.create_table_extractor()
            storage = factory.create_storage_adapter(self.results_directory)
            
            # 4. Ejecutar procesamiento
            process_doc = ProcessDocument(ocr, table_extractor, storage)
            
            print(f"\nProcesando documento...")
            print(f"Archivo: {selected_pdf.name}")
            
            document = process_doc.execute(selected_pdf)
            
            # 5. Mostrar resultados
            print(f"\nProceso completado exitosamente!")
            print(f"Documento: {document.name}")
            print(f"Texto extraído: {len(document.extracted_text):,} caracteres")
            print(f"Tablas encontradas: {len(document.tables)}")
            print(f"Directorio de salida: {document.output_directory.name}")
            print(f"Archivos generados: {len(document.generated_files)}")
            
            # Mostrar si se usó nombre único
            if document.name != selected_pdf.stem:
                print(f"NOTA: Se asignó nombre único '{document.name}' para evitar duplicados")
            
            print(f"\nArchivos guardados:")
            for file_path in document.generated_files:
                print(f"   {file_path.name}")
            
            return document
            
        except DomainError as e:
            logger.error(f"Error del dominio: {str(e)}")
            print(f"\nERROR: Error de procesamiento: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            print(f"\nERROR: Error inesperado: {str(e)}")
            return None

    def show_system_configuration(self):
        """Mostrar configuración actual del sistema."""
        print("\nCONFIGURACION DEL SISTEMA")
        print("-" * 40)
        print(f"Motor OCR: {self.config.engine_type}")
        print(f"Idioma: {self.config.language}")
        print(f"DPI: {self.config.dpi}")
        print(f"Umbral de confianza: {self.config.confidence_threshold}%")
        print(f"Directorio de PDFs: {self.pdfs_directory}")
        print(f"Directorio de resultados: {self.results_directory}")
        
        if hasattr(self.config, 'enable_deskewing'):
            status_deskew = "Activada" if self.config.enable_deskewing else "Desactivada"
            print(f"Corrección de inclinación: {status_deskew}")
        if hasattr(self.config, 'enable_denoising'):
            status_denoise = "Activada" if self.config.enable_denoising else "Desactivada"
            print(f"Eliminación de ruido: {status_denoise}")
        if hasattr(self.config, 'enable_contrast_enhancement'):
            status_contrast = "Activada" if self.config.enable_contrast_enhancement else "Desactivada"
            print(f"Mejora de contraste: {status_contrast}")

    def list_available_files(self):
        """Listar archivos PDF disponibles."""
        pdf_files = self.discover_pdfs()
        
        print("\nARCHIVOS PDF DISPONIBLES")
        print("-" * 40)
        
        if not pdf_files:
            print("ERROR: No se encontraron archivos PDF")
            print("NOTA: Coloque archivos PDF en el directorio ./pdfs/")
        else:
            for i, pdf_file in enumerate(pdf_files, 1):
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f"{i:2d}. {pdf_file.name} ({size_mb:.1f} MB)")

    def list_previous_results(self):
        """Listar resultados anteriores."""
        print("\nRESULTADOS ANTERIORES")
        print("-" * 40)
        
        try:
            if not self.results_directory.exists():
                print("ERROR: No se encontró directorio de resultados")
                return
            
            result_dirs = [d for d in self.results_directory.iterdir() if d.is_dir()]
            
            if not result_dirs:
                print("ERROR: No se encontraron resultados anteriores")
            else:
                for i, result_dir in enumerate(result_dirs, 1):
                    metadata_file = result_dir / f"{result_dir.name}_metadata.json"
                    if metadata_file.exists():
                        print(f"{i:2d}. {result_dir.name}/")
                    else:
                        print(f"{i:2d}. {result_dir.name}/ (sin metadatos)")
                        
        except Exception as e:
            logger.error(f"Error listando resultados: {str(e)}")
            print(f"ERROR: Error accediendo a resultados: {str(e)}")

    def configure_system(self):
        """Configurar parámetros del sistema."""
        print("\nCONFIGURACION DEL SISTEMA")
        print("-" * 40)
        print("1. Cambiar motor OCR")
        print("2. Cambiar idioma")
        print("3. Ajustar DPI")
        print("4. Volver al menú principal")
        
        choice = self.get_user_choice(4)
        
        if choice == 1:
            new_config = self.select_ocr_engine()
            if new_config:
                self.config = new_config
                print("Configuración actualizada")
        elif choice == 2:
            print("\nIdiomas disponibles:")
            print("1. Español (spa)")
            print("2. Inglés (eng)")
            print("3. Portugués (por)")
            
            lang_choice = self.get_user_choice(3)
            lang_map = {1: "spa", 2: "eng", 3: "por"}
            self.config.language = lang_map.get(lang_choice, "spa")
            print(f"Idioma cambiado a: {self.config.language}")
            
        elif choice == 3:
            try:
                new_dpi = int(input("Ingrese nuevo DPI (150-600): "))
                if 150 <= new_dpi <= 600:
                    self.config.dpi = new_dpi
                    print(f"DPI cambiado a: {new_dpi}")
                else:
                    print("ERROR: DPI debe estar entre 150 y 600")
            except ValueError:
                print("ERROR: Valor de DPI inválido")

    def run(self):
        """Ejecutar el menú interactivo principal."""
        while self.running:
            try:
                self.clear_screen()
                self.show_header()
                self.show_main_menu()
                
                choice = self.get_user_choice(6)
                
                if choice == 1:
                    self.process_document()
                elif choice == 2:
                    self.configure_system()
                elif choice == 3:
                    self.show_system_configuration()
                elif choice == 4:
                    self.list_available_files()
                elif choice == 5:
                    self.list_previous_results()
                elif choice == 6:
                    print("\nGracias por usar el Sistema OCR!")
                    self.running = False
                    break
                
                if choice != 6:
                    input("\nPresione Enter para continuar...")
                    
            except KeyboardInterrupt:
                print("\n\nSaliendo del sistema...")
                self.running = False
            except Exception as e:
                logger.error(f"Error en menú principal: {str(e)}")
                print(f"\nERROR: Error inesperado: {str(e)}")
                input("\nPresione Enter para continuar...")


def main():
    """Punto de entrada principal del menú interactivo."""
    menu = InteractiveMenu()
    menu.run()


if __name__ == "__main__":
    main()