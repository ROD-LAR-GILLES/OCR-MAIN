"""
Script para comparar resultados antes y después de la refactorización.
"""
import subprocess
import tempfile
import shutil
import hashlib
from pathlib import Path
import json

def get_file_hash(file_path):
    """Calcula el hash MD5 de un archivo."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def compare_results(original_dir, new_dir):
    """Compara los resultados de procesamiento."""
    results = {
        "matching_files": 0,
        "different_files": 0,
        "missing_files": 0,
        "extra_files": 0,
        "differences": []
    }
    
    # Obtener todos los archivos en el directorio original
    original_files = list(Path(original_dir).glob("**/*"))
    original_files = [f for f in original_files if f.is_file()]
    
    # Obtener todos los archivos en el nuevo directorio
    new_files = list(Path(new_dir).glob("**/*"))
    new_files = [f for f in new_files if f.is_file()]
    
    # Comparar archivos
    for orig_file in original_files:
        rel_path = orig_file.relative_to(original_dir)
        new_file = Path(new_dir) / rel_path
        
        if not new_file.exists():
            results["missing_files"] += 1
            results["differences"].append(f"Falta: {rel_path}")
            continue
        
        # Comparar contenido
        orig_hash = get_file_hash(orig_file)
        new_hash = get_file_hash(new_file)
        
        if orig_hash == new_hash:
            results["matching_files"] += 1
        else:
            results["different_files"] += 1
            results["differences"].append(f"Diferente: {rel_path}")
    
    # Verificar archivos extra
    for new_file in new_files:
        rel_path = new_file.relative_to(new_dir)
        orig_file = Path(original_dir) / rel_path
        
        if not orig_file.exists():
            results["extra_files"] += 1
            results["differences"].append(f"Extra: {rel_path}")
    
    return results

def main():
    # Crear directorios temporales
    old_output = Path(tempfile.mkdtemp())
    new_output = Path(tempfile.mkdtemp())
    
    try:
        test_pdf = "e7a25f50-fad_pdf_digital.pdf"
        
        # Procesar con versión anterior (asumiendo que tienes un commit previo)
        subprocess.run(["git", "checkout", "HEAD~1", "--", "src/"])
        subprocess.run(["./restart.sh", "basic", test_pdf, "--output", str(old_output)])
        
        # Procesar con nueva versión
        subprocess.run(["git", "checkout", "HEAD", "--", "src/"])
        subprocess.run(["./restart.sh", "basic", test_pdf, "--output", str(new_output)])
        
        # Comparar resultados
        results = compare_results(old_output, new_output)
        
        # Mostrar resultados
        print(json.dumps(results, indent=2))
        
        if results["different_files"] == 0 and results["missing_files"] == 0:
            print("\n✅ Refactorización exitosa! Los resultados son idénticos.")
        else:
            print("\n❌ Hay diferencias en los resultados.")
    
    finally:
        # Limpiar
        shutil.rmtree(old_output)
        shutil.rmtree(new_output)

if __name__ == "__main__":
    main()