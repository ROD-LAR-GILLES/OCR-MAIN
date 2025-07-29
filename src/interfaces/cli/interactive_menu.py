"""
Menú interactivo para el sistema OCR.
"""
import os
import logging
from pathlib import Path
from typing import Optional

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


class InteractiveMenu:
    """Menú interactivo para el sistema OCR."""
    
    def __init__(self):
        self.config = SystemConfig()
        self.running = True
    
    def clear_screen(self):
        """Limpia la pantalla."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Muestra el encabezado del sistema."""
        print("=" * 60)
        print("               SISTEMA OCR - CLEAN ARCHITECTURE")
        print("=" * 60)
        print()
    
    def show_main_menu(self):
        """Muestra el menú principal."""
        print("MENU PRINCIPAL")
        print("-" * 20)
        print("1. Procesar documento PDF")
        print("2. Configurar sistema")
        print("3. Ver estado del sistema")
        print("4. Listar archivos disponibles")
        print("5. Ver resultados anteriores")
        print("0. Salir")
        print()
    
    def show_engine_menu(self):
        """Muestra el menú de selección de motor OCR."""
        print("SELECCIONAR MOTOR OCR")
        print("-" * 20)
        print("1. Motor básico (rapido)")
        print("2. Motor OpenCV (mejor calidad)")
        print("0. Volver")
        print()
    
    def show_config_menu(self):
        """Muestra el menú de configuración."""
        print("CONFIGURACION DEL SISTEMA")
        print("-" * 25)
        print(f"Motor actual: {self.config.engine_type}")
        print(f"Idioma: {self.config.language}")
        print(f"DPI: {self.config.dpi}")
        print(f"Directorio salida: {self.config.output_dir}")
        print()
        print("1. Cambiar motor OCR")
        print("2. Cambiar idioma")
        print("3. Cambiar DPI")
        print("4. Cambiar directorio de salida")
        print("0. Volver")
        print()
    
    def get_user_input(self, prompt: str) -> str:
        """Obtiene entrada del usuario."""
        return input(f"{prompt}: ").strip()
    
    def get_pdf_files(self) -> list:
        """Obtiene lista de archivos PDF disponibles."""
        pdf_dir = Path("pdfs")
        if not pdf_dir.exists():
            return []
        return [f.name for f in pdf_dir.glob("*.pdf")]
    
    def list_pdf_files(self):
        """Lista archivos PDF disponibles."""
        files = self.get_pdf_files()
        if not files:
            print("No hay archivos PDF en la carpeta 'pdfs'")
            return
        
        print("ARCHIVOS PDF DISPONIBLES")
        print("-" * 25)
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        print()
    
    def list_results(self):
        """Lista resultados anteriores."""
        result_dir = Path(self.config.output_dir)
        if not result_dir.exists():
            print("No hay resultados anteriores")
            return
        
        files = list(result_dir.glob("*"))
        if not files:
            print("No hay resultados anteriores")
            return
        
        print("RESULTADOS ANTERIORES")
        print("-" * 20)
        for file in files:
            print(f"- {file.name}")
        print()
    
    def select_pdf_file(self) -> Optional[Path]:
        """Permite al usuario seleccionar un archivo PDF."""
        files = self.get_pdf_files()
        if not files:
            print("No hay archivos PDF disponibles")
            input("Presiona Enter para continuar...")
            return None
        
        self.list_pdf_files()
        
        try:
            choice = int(self.get_user_input("Selecciona un archivo (numero)"))
            if 1 <= choice <= len(files):
                return Path("pdfs") / files[choice - 1]
            else:
                print("Seleccion invalida")
                return None
        except ValueError:
            print("Por favor ingresa un numero valido")
            return None
    
    def select_engine(self) -> str:
        """Permite al usuario seleccionar el motor OCR."""
        while True:
            self.clear_screen()
            self.show_header()
            self.show_engine_menu()
            
            choice = self.get_user_input("Selecciona una opcion")
            
            if choice == "1":
                return "basic"
            elif choice == "2":
                return "opencv"
            elif choice == "0":
                return self.config.engine_type
            else:
                print("Opcion invalida")
                input("Presiona Enter para continuar...")
    
    def process_document(self):
        """Procesa un documento seleccionado."""
        try:
            # Seleccionar PDF
            pdf_files = self.discover_pdfs()
            if not pdf_files:
                print("\n No se encontraron archivos PDF en el directorio ./pdfs/")
                return
            
            # Seleccionar archivo
            pdf_path = self.select_pdf_file()
            if not pdf_path:
                return
            
            # Seleccionar motor
            engine = self.select_engine()
            
            print(f"\nProcesando: {pdf_path.name}")
            print(f"Motor: {engine}")
            print("-" * 40)
            
            # Actualizar configuración
            self.config.engine_type = engine
            
            # Crear adaptadores
            factory = AdapterFactory()
            ocr = factory.create_ocr_adapter(self.config)
            table_extractor = factory.create_table_extractor()
            storage = factory.create_storage_adapter(self.config.output_dir)
            
            # Crear caso de uso
            process_doc = ProcessDocument(ocr, table_extractor, storage)
            
            # Procesar documento
            document = process_doc.execute(pdf_path)
            
            print(f"\n Proceso completado exitosamente!")
            print(f" Documento: {document.name}")  # Ahora muestra el nombre único
            print(f" Texto extraído: {len(document.extracted_text)} caracteres")
            print(f" Tablas encontradas: {len(document.tables)}")
            print(f" Resultados guardados en: {document.output_directory}")
            print(f" Archivos generados: {len(document.generated_files)}")
            
            if document.name != pdf_path.stem:
                print(f" Nota: Se asignó nombre único '{document.name}' para evitar duplicados")
            
            return document
            
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            print(f"\n Error inesperado: {str(e)}")
            return None
    
    def configure_system(self):
        """Configura el sistema."""
        while True:
            self.clear_screen()
            self.show_header()
            self.show_config_menu()
            
            choice = self.get_user_input("Selecciona una opcion")
            
            if choice == "1":
                engine = self.select_engine()
                self.config.engine_type = engine
                print(f"Motor cambiado a: {engine}")
                input("Presiona Enter para continuar...")
            elif choice == "2":
                lang = self.get_user_input("Nuevo idioma (spa, eng, etc)")
                if lang:
                    self.config.language = lang
                    print(f"Idioma cambiado a: {lang}")
                input("Presiona Enter para continuar...")
            elif choice == "3":
                try:
                    dpi = int(self.get_user_input("Nuevo DPI (150, 300, 600)"))
                    self.config.dpi = dpi
                    print(f"DPI cambiado a: {dpi}")
                except ValueError:
                    print("DPI invalido")
                input("Presiona Enter para continuar...")
            elif choice == "4":
                output_dir = self.get_user_input("Nuevo directorio de salida")
                if output_dir:
                    self.config.output_dir = Path(output_dir)
                    print(f"Directorio cambiado a: {output_dir}")
                input("Presiona Enter para continuar...")
            elif choice == "0":
                break
            else:
                print("Opcion invalida")
                input("Presiona Enter para continuar...")
    
    def show_system_status(self):
        """Muestra el estado del sistema."""
        self.clear_screen()
        self.show_header()
        
        print("ESTADO DEL SISTEMA")
        print("-" * 18)
        print(f"Motor OCR: {self.config.engine_type}")
        print(f"Idioma: {self.config.language}")
        print(f"DPI: {self.config.dpi}")
        print(f"Umbral confianza: {self.config.confidence_threshold}")
        print(f"Directorio salida: {self.config.output_dir}")
        print(f"Directorio temporal: {self.config.temp_dir}")
        
        # Verificar directorios
        print("\nESTADO DE DIRECTORIOS")
        print("-" * 20)
        pdf_dir = Path("pdfs")
        print(f"Carpeta PDFs: {'OK' if pdf_dir.exists() else 'NO EXISTE'}")
        print(f"Carpeta resultados: {'OK' if self.config.output_dir.exists() else 'NO EXISTE'}")
        
        # Contar archivos
        pdf_count = len(self.get_pdf_files())
        print(f"Archivos PDF disponibles: {pdf_count}")
        
        input("\nPresiona Enter para continuar...")
    
    def run(self):
        """Ejecuta el menú principal."""
        while self.running:
            self.clear_screen()
            self.show_header()
            self.show_main_menu()
            
            choice = self.get_user_input("Selecciona una opcion")
            
            if choice == "1":
                self.process_document()
            elif choice == "2":
                self.configure_system()
            elif choice == "3":
                self.show_system_status()
            elif choice == "4":
                self.clear_screen()
                self.show_header()
                self.list_pdf_files()
                input("Presiona Enter para continuar...")
            elif choice == "5":
                self.clear_screen()
                self.show_header()
                self.list_results()
                input("Presiona Enter para continuar...")
            elif choice == "0":
                print("Saliendo del sistema...")
                self.running = False
            else:
                print("Opcion invalida")
                input("Presiona Enter para continuar...")


def main():
    """Punto de entrada principal."""
    menu = InteractiveMenu()
    menu.run()


if __name__ == "__main__":
    main()