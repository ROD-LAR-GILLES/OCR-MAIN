#!/bin/bash

echo " Sistema OCR - Clean Architecture"
echo "=================================="

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN] [ARCHIVO_PDF]"
    echo ""
    echo "Opciones:"
    echo "  help          Mostrar esta ayuda"
    echo "  build         Construir imagen Docker"
    echo "  menu          Iniciar menú interactivo"
    echo "  basic FILE    Procesar con motor básico"
    echo "  opencv FILE   Procesar con motor OpenCV"
    echo "  test          Ejecutar pruebas"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build"
    echo "  $0 menu"
    echo "  $0 basic documento.pdf"
    echo "  $0 opencv documento.pdf"
}

# Función para construir imagen
build_image() {
    echo " Construyendo imagen Docker..."
    docker-compose build
}

# Función para iniciar menú interactivo
start_menu() {
    echo " Iniciando menú interactivo..."
    docker-compose run --rm ocr python -m interfaces.cli.interactive_menu
}

# Función para procesar con motor básico
process_basic() {
    local file=$1
    if [ -z "$file" ]; then
        echo " Error: Especifica un archivo PDF"
        show_help
        exit 1
    fi
    
    echo " Procesando $file con motor básico..."
    docker-compose run --rm ocr python -m interfaces.cli.menu "/app/pdfs/$file" --engine basic --verbose
}

# Función para procesar con OpenCV
process_opencv() {
    local file=$1
    if [ -z "$file" ]; then
        echo " Error: Especifica un archivo PDF"
        show_help
        exit 1
    fi
    
    echo " Procesando $file con motor OpenCV..."
    docker-compose run --rm ocr python -m interfaces.cli.menu "/app/pdfs/$file" --engine opencv --verbose
}

# Función para ejecutar pruebas
run_tests() {
    echo " Ejecutando pruebas..."
    docker-compose run --rm ocr python -c "
    print(' Importaciones funcionando')
    from interfaces.cli.menu import main
    from application.use_cases import ProcessDocument
    print(' Todas las importaciones exitosas')
    "
}

# Procesamiento de argumentos
case "$1" in
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    "build")
        build_image
        ;;
    "menu")
        start_menu
        ;;
    "basic")
        process_basic "$2"
        ;;
    "opencv")
        process_opencv "$2"
        ;;
    "test")
        run_tests
        ;;
    *)
        echo " Opción desconocida: $1"
        show_help
        exit 1
        ;;
esac