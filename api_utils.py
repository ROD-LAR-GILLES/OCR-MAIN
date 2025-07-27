"""
Utilidades para la API FastAPI.
"""
import requests
import json
import sys
from pathlib import Path
from typing import Optional
import time


class OCRAPIClient:
    """Cliente para interactuar con la API OCR."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Inicializa el cliente."""
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
    
    def health_check(self) -> dict:
        """Verifica el estado de salud de la API."""
        try:
            response = requests.get(f"{self.api_base}/health/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def get_system_status(self) -> dict:
        """Obtiene el estado del sistema."""
        try:
            response = requests.get(f"{self.api_base}/status/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def upload_document(self, file_path: Path, config: Optional[dict] = None) -> dict:
        """
        Sube y procesa un documento.
        
        Args:
            file_path: Ruta al archivo PDF
            config: Configuración opcional para el procesamiento
            
        Returns:
            Respuesta con job_id para seguimiento
        """
        if not file_path.exists():
            return {"error": f"Archivo no encontrado: {file_path}"}
        
        if not file_path.suffix.lower() == '.pdf':
            return {"error": "Solo se aceptan archivos PDF"}
        
        try:
            # Preparar archivos y datos
            files = {"file": (file_path.name, open(file_path, "rb"), "application/pdf")}
            data = config or {}
            
            # Hacer request
            response = requests.post(
                f"{self.api_base}/documents/upload",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            return {"error": str(e)}
        finally:
            # Cerrar archivo
            if 'files' in locals():
                files["file"][1].close()
    
    def get_processing_status(self, job_id: str) -> dict:
        """Obtiene el estado de procesamiento de un job."""
        try:
            response = requests.get(f"{self.api_base}/documents/status/{job_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def wait_for_completion(self, job_id: str, timeout: int = 300) -> dict:
        """
        Espera a que complete el procesamiento.
        
        Args:
            job_id: ID del job a monitorear
            timeout: Timeout en segundos
            
        Returns:
            Estado final del procesamiento
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_processing_status(job_id)
            
            if "error" in status:
                return status
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "error":
                return status
            
            print(f"⏳ Progreso: {status.get('progress', 0):.1f}% - {status.get('message', '')}")
            time.sleep(2)
        
        return {"error": "Timeout esperando completion", "timeout": timeout}
    
    def download_file(self, job_id: str, file_type: str, output_path: Optional[Path] = None) -> bool:
        """
        Descarga un archivo procesado.
        
        Args:
            job_id: ID del job
            file_type: Tipo de archivo (text, summary, metadata, original)
            output_path: Ruta donde guardar (opcional)
            
        Returns:
            True si se descargó correctamente
        """
        try:
            response = requests.get(f"{self.api_base}/documents/{job_id}/download/{file_type}")
            response.raise_for_status()
            
            # Determinar nombre de archivo
            if output_path is None:
                filename = response.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')
                if not filename:
                    filename = f"{job_id}_{file_type}"
                output_path = Path(filename)
            
            # Guardar archivo
            output_path.write_bytes(response.content)
            print(f" Archivo descargado: {output_path}")
            return True
            
        except requests.RequestException as e:
            print(f" Error descargando archivo: {e}")
            return False
    
    def process_document_complete(self, file_path: Path, config: Optional[dict] = None) -> dict:
        """
        Procesa un documento completamente (upload + wait + status).
        
        Args:
            file_path: Ruta al archivo PDF
            config: Configuración opcional
            
        Returns:
            Resultado final del procesamiento
        """
        print(f" Subiendo archivo: {file_path.name}")
        
        # Upload
        upload_result = self.upload_document(file_path, config)
        if "error" in upload_result:
            return upload_result
        
        job_id = upload_result.get("job_id")  # Nota: verificar el campo correcto en la respuesta
        if not job_id:
            return {"error": "No se recibió job_id"}
        
        print(f" Job ID: {job_id}")
        
        # Wait for completion
        final_status = self.wait_for_completion(job_id)
        
        if final_status.get("status") == "completed":
            print(f" Procesamiento completado!")
            document = final_status.get("document", {})
            print(f" Documento: {document.get('name', 'N/A')}")
            print(f" Confianza: {document.get('confidence', 'N/A')}")
            print(f" Directorio: {document.get('output_directory', 'N/A')}")
        
        return final_status


def main():
    """CLI para interactuar con la API."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cliente CLI para OCR API")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base de la API")
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    # Health check
    subparsers.add_parser("health", help="Verificar estado de la API")
    
    # Status
    subparsers.add_parser("status", help="Estado del sistema")
    
    # Process document
    process_parser = subparsers.add_parser("process", help="Procesar documento")
    process_parser.add_argument("file", type=Path, help="Archivo PDF a procesar")
    process_parser.add_argument("--engine", choices=["basic", "opencv", "auto"], default="auto")
    process_parser.add_argument("--language", default="spa")
    process_parser.add_argument("--dpi", type=int, default=300)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Crear cliente
    client = OCRAPIClient(args.url)
    
    # Ejecutar comando
    if args.command == "health":
        result = client.health_check()
        print(json.dumps(result, indent=2))
    
    elif args.command == "status":
        result = client.get_system_status()
        print(json.dumps(result, indent=2))
    
    elif args.command == "process":
        config = {
            "engine_type": args.engine,
            "language": args.language,
            "dpi": args.dpi
        }
        result = client.process_document_complete(args.file, config)
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()