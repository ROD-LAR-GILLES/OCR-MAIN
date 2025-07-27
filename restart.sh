#!/bin/bash

echo "============================================================"
echo "SISTEMA OCR - CLEAN ARCHITECTURE v2.0.0"
echo "============================================================"

# Detectar si la terminal soporta colores
if [ -t 1 ] && command -v tput >/dev/null 2>&1 && tput colors >/dev/null 2>&1 && [ "$(tput colors)" -ge 8 ]; then
    # Colores para output
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    NC='\033[0m' # No Color
else
    # Sin colores
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    PURPLE=''
    CYAN=''
    NC=''
fi

# Función para mostrar ayuda
show_help() {
    echo ""
    echo "Uso: $0 [OPCIÓN] [ARCHIVO_PDF]"
    echo ""
    echo "OPCIONES CLI:"
    echo "  help          - Mostrar esta ayuda"
    echo "  build         - Construir imagen Docker"
    echo "  menu          - Iniciar menú interactivo"
    echo "  basic FILE    - Procesar con motor básico"
    echo "  opencv FILE   - Procesar con motor OpenCV"
    echo "  test          - Ejecutar pruebas del sistema"
    echo "  logs          - Ver logs en tiempo real"
    echo "  clean         - Limpiar sistema y contenedores"
    echo "  restart       - Reiniciar API sin rebuild"
    echo "  restart-build - Reiniciar API con rebuild"
    echo ""
    echo "OPCIONES API REST:"
    echo "  api           - Iniciar API FastAPI"
    echo "  api-prod      - Iniciar API FastAPI (producción)"
    echo "  api-nginx     - Iniciar API con Docker + Nginx"
    echo "  test-api      - Probar endpoints de la API"
    echo "  stop-api      - Detener servicios de la API"
    echo ""
    echo "UTILIDADES:"
    echo "  status        - Estado del sistema"
    echo "  docs          - Abrir documentación de la API"
    echo ""
    echo "Ejemplos:"
    echo "  $0 build"
    echo "  $0 menu"
    echo "  $0 api"
    echo "  $0 restart"
    echo "  $0 restart-build"
    echo "  $0 basic documento.pdf"
    echo "  $0 test-api"
}

# ========== NUEVA FUNCIÓN RESTART ==========

# Función para reiniciar API simple
restart_api() {
    echo "${BLUE}[RESTART] Reiniciando OCR Processing API...${NC}"
    
    # Crear directorios si no existen
    echo "${CYAN}[SETUP] Verificando directorios...${NC}"
    mkdir -p pdfs resultado logs
    
    # Dar permisos
    chmod 755 pdfs resultado logs
    echo "${GREEN}[OK] Directorios verificados/creados${NC}"
    
    # Parar contenedores
    echo "${YELLOW}[STOP] Deteniendo contenedores...${NC}"
    docker-compose down
    
    # Rebuild si se especifica
    if [ "$1" = "build" ]; then
        echo "${BLUE}[BUILD] Reconstruyendo imagen...${NC}"
        docker-compose build --no-cache
    fi
    
    # Iniciar contenedores
    echo "${GREEN}[START] Iniciando contenedores...${NC}"
    docker-compose up -d
    
    # Esperar a que el servicio esté listo
    echo "${CYAN}[WAIT] Esperando a que el servicio esté listo...${NC}"
    sleep 5
    
    # Verificar estado
    echo "${BLUE}[CHECK] Verificando estado...${NC}"
    if curl -s "http://localhost:8000/api/v1/health/" > /dev/null 2>&1; then
        echo "${GREEN}[OK] Servicio disponible en http://localhost:8000${NC}"
        echo "${CYAN}[INFO] Documentación: http://localhost:8000/api/v1/docs${NC}"
    else
        echo "${RED}[ERROR] Servicio no disponible aún${NC}"
        echo "${YELLOW}[INFO] Verificando logs...${NC}"
    fi
    
    echo ""
    echo "${CYAN}[LOGS] Últimos logs del contenedor:${NC}"
    docker logs ocr-processing-api --tail 10
    
    echo ""
    echo "${GREEN}[OK] Proceso completado${NC}"
}

# Función para crear directorios necesarios
ensure_directories() {
    mkdir -p pdfs resultado logs
    echo "${GREEN}[OK] Directorios creados/verificados${NC}"
}

# Función para construir imagen
build_image() {
    echo "${BLUE}[BUILD] Construyendo imagen Docker...${NC}"
    ensure_directories
    docker-compose build
    echo "${GREEN}[OK] Imagen construida exitosamente${NC}"
}

# Función para iniciar menú interactivo CLI
start_menu() {
    echo "${BLUE}[CLI] Iniciando menú interactivo...${NC}"
    ensure_directories
    docker-compose run --rm ocr-processing-api python -m interfaces.cli.interactive_menu
}

# Función para procesar con motor básico
process_basic() {
    local file=$1
    if [ -z "$file" ]; then
        echo "${RED}[ERROR] Especifica un archivo PDF${NC}"
        show_help
        exit 1
    fi
    
    echo "${BLUE}[PROCESS] Procesando $file con motor básico...${NC}"
    ensure_directories
    docker-compose run --rm ocr-processing-api python -m interfaces.cli.menu "/app/pdfs/$file" --engine basic --verbose
}

# Función para procesar con OpenCV
process_opencv() {
    local file=$1
    if [ -z "$file" ]; then
        echo "${RED}[ERROR] Especifica un archivo PDF${NC}"
        show_help
        exit 1
    fi
    
    echo "${BLUE}[PROCESS] Procesando $file con motor OpenCV...${NC}"
    ensure_directories
    docker-compose run --rm ocr-processing-api python -m interfaces.cli.menu "/app/pdfs/$file" --engine opencv --verbose
}

# Función para ejecutar pruebas
run_tests() {
    echo "${BLUE}[TEST] Ejecutando pruebas del sistema...${NC}"
    ensure_directories
    docker-compose up ocr-processing-api python -c "
    print('[TEST] Verificando importaciones...')
    try:
        from interfaces.cli.menu import main
        from application.use_cases import ProcessDocument
        from domain.models import Document
        from infrastructure.config.system_config import SystemConfig
        print('[OK] Todas las importaciones exitosas')
        print('[OK] Sistema listo para funcionar')
    except Exception as e:
        print(f'[ERROR] Error en importaciones: {e}')
        exit(1)
    "
}

# ========== FUNCIONES API FASTAPI (SOLO DOCKER) ==========

# Función para iniciar API en desarrollo
start_api_dev() {
    echo "${GREEN}[API] Iniciando API FastAPI (modo desarrollo)...${NC}"
    ensure_directories
    
    echo "${CYAN}[DOCKER] Usando Docker para la API${NC}"
    echo "${CYAN}[DEV] Modo desarrollo - Auto-reload habilitado${NC}"
    echo "${CYAN}[INFO] Documentación: http://localhost:8000/docs${NC}"
    echo "${CYAN}[INFO] ReDoc: http://localhost:8000/redoc${NC}"
    
    # Ejecutar con Docker y reload
    docker-compose run --rm -p 8000:8000 ocr-api python run_api.py --host 0.0.0.0 --reload --log-level debug --access-log
}

# Función para iniciar API en producción
start_api_prod() {
    echo "${GREEN}[API] Iniciando API FastAPI (modo producción)...${NC}"
    ensure_directories
    
    echo "${CYAN}[DOCKER] Usando Docker para la API${NC}"
    echo "${CYAN}[PROD] Modo producción - 4 workers${NC}"
    
    # Ejecutar con Docker en modo producción
    docker-compose run --rm -p 8000:8000 ocr-api python run_api.py --host 0.0.0.0 --workers 4 --log-level info
}

# Función para iniciar API con Docker Compose
start_api_docker() {
    echo "${GREEN}[API] Iniciando API con Docker Compose...${NC}"
    ensure_directories
    
    echo "${CYAN}[INFO] Documentación: http://localhost:8000/api/v1/docs${NC}"
    echo "${CYAN}[INFO] ReDoc: http://localhost:8000/api/v1/redoc${NC}"
    
    docker-compose up --build ocr-processing-api
}

# Función para iniciar API con Docker + Nginx
start_api_nginx() {
    echo "${GREEN}[API] Iniciando API con Docker + Nginx...${NC}"
    ensure_directories
    
    echo "${CYAN}[NGINX] Acceso via Nginx: http://localhost${NC}"
    echo "${CYAN}[INFO] Documentación: http://localhost/docs${NC}"
    echo "${CYAN}[INFO] ReDoc: http://localhost/redoc${NC}"
    
    docker-compose --profile production up --build
}

# Función para probar la API
test_api() {
    echo "${BLUE}[TEST] Probando OCR Processing API...${NC}"
    
    API_URL="http://localhost:8000"
    
    # Verificar si curl está disponible
    if ! command -v curl &> /dev/null; then
        echo "${RED}[ERROR] curl no está instalado${NC}"
        exit 1
    fi
    
    # Test 1: Health check
    echo ""
    echo "${CYAN}[1/3] Health Check:${NC}"
    if curl -s "$API_URL/api/v1/health/" | python3 -m json.tool 2>/dev/null; then
        echo "${GREEN}[OK] Health check exitoso${NC}"
    else
        echo "${RED}[ERROR] API no responde. Está iniciada?${NC}"
        echo "${YELLOW}[TIP] Ejecuta: $0 api${NC}"
        exit 1
    fi
    
    # Test 2: System Status
    echo ""
    echo "${CYAN}[2/3] System Status:${NC}"
    curl -s "$API_URL/api/v1/status/" | python3 -m json.tool
    
    # Test 3: Upload documento (si existe un PDF de prueba)
    echo ""
    if [ -f "pdfs/pdf_escrito.pdf" ]; then
        echo "${CYAN}[3/3] Upload Test Document (pdf_escrito.pdf):${NC}"
        curl -s -X POST \
            -F "file=@pdfs/pdf_escrito.pdf" \
            -F "engine_type=basic" \
            "$API_URL/api/v1/documents/upload" | python3 -m json.tool
    elif [ -f "pdfs/test.pdf" ]; then
        echo "${CYAN}[3/3] Upload Test Document (test.pdf):${NC}"
        curl -s -X POST \
            -F "file=@pdfs/test.pdf" \
            -F "engine_type=basic" \
            "$API_URL/api/v1/documents/upload" | python3 -m json.tool
    else
        echo "${YELLOW}[3/3] No se encontró PDF de prueba en pdfs/${NC}"
        echo "${YELLOW}[TIP] Coloca un PDF en pdfs/ para probar upload${NC}"
    fi
    
    echo ""
    echo "${GREEN}[OK] Pruebas completadas${NC}"
    echo "${CYAN}[INFO] Documentación: $API_URL/docs${NC}"
    echo "${CYAN}[INFO] ReDoc: $API_URL/redoc${NC}"
}

# Función para detener servicios API
stop_api() {
    echo "${YELLOW}[STOP] Deteniendo servicios de la API...${NC}"
    docker-compose down
    echo "${GREEN}[OK] Servicios detenidos${NC}"
}

# ========== FUNCIONES UTILIDADES ==========

# Función para mostrar estado del sistema
show_status() {
    echo "${BLUE}[STATUS] Estado del Sistema OCR${NC}"
    echo ""
    
    # Estado de Docker
    echo "${CYAN}Docker:${NC}"
    if command -v docker &> /dev/null; then
        echo "  [OK] Docker instalado"
        if docker ps &> /dev/null; then
            echo "  [OK] Docker ejecutándose"
        else
            echo "  [ERROR] Docker no está ejecutándose"
        fi
    else
        echo "  [ERROR] Docker no instalado"
    fi
    
    # Estado de directorios
    echo ""
    echo "${CYAN}Directorios:${NC}"
    [ -d "pdfs" ] && echo "  [OK] pdfs/" || echo "  [ERROR] pdfs/"
    [ -d "resultado" ] && echo "  [OK] resultado/" || echo "  [ERROR] resultado/"
    [ -d "src" ] && echo "  [OK] src/" || echo "  [ERROR] src/"
    
    # Archivos PDF disponibles
    echo ""
    echo "${CYAN}PDFs disponibles:${NC}"
    if [ -d "pdfs" ] && [ "$(ls -A pdfs/*.pdf 2>/dev/null)" ]; then
        ls -la pdfs/*.pdf | while read line; do
            echo "  [FILE] $(echo $line | awk '{print $9}') ($(echo $line | awk '{print $5}') bytes)"
        done
    else
        echo "  [EMPTY] No hay PDFs en pdfs/"
    fi
    
    # Documentos procesados
    echo ""
    echo "${CYAN}Documentos procesados:${NC}"
    if [ -d "resultado" ] && [ "$(ls -A resultado/ 2>/dev/null)" ]; then
        ls -la resultado/ | grep "^d" | wc -l | xargs echo "  [COUNT] Total:" 
        ls resultado/ | head -5 | while read dir; do
            echo "  [DIR] $dir"
        done
    else
        echo "  [EMPTY] No hay documentos procesados"
    fi
    
    # Estado de la API
    echo ""
    echo "${CYAN}API Status:${NC}"
    if curl -s http://localhost:8000/api/v1/health/ &> /dev/null; then
        echo "  [RUNNING] API ejecutándose en http://localhost:8000"
    else
        echo "  [STOPPED] API no responde"
    fi
}

# Función para ver logs
show_logs() {
    echo "${BLUE}[LOGS] Mostrando logs en tiempo real...${NC}"
    echo "${YELLOW}[INFO] Presiona Ctrl+C para salir${NC}"
    echo ""
    docker-compose logs -f
}

# Función para limpiar sistema
clean_system() {
    echo "${YELLOW}[CLEAN] Limpiando sistema...${NC}"
    
    read -p "Eliminar contenedores Docker? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --rmi all --volumes
        echo "${GREEN}[OK] Contenedores eliminados${NC}"
    fi
    
    read -p "Eliminar resultados procesados? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf resultado/*
        echo "${GREEN}[OK] Resultados eliminados${NC}"
    fi
    
    read -p "Eliminar logs? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf logs/*
        echo "${GREEN}[OK] Logs eliminados${NC}"
    fi
    
    echo "${GREEN}[OK] Limpieza completada${NC}"
}

# Función para abrir documentación
open_docs() {
    API_URL="http://localhost:8000"
    echo "${BLUE}[DOCS] Abriendo documentación de la API...${NC}"
    
    # Verificar si la API está ejecutándose
    if ! curl -s "$API_URL/api/v1/health/" &> /dev/null; then
        echo "${RED}[ERROR] API no está ejecutándose${NC}"
        echo "${YELLOW}[TIP] Ejecuta: $0 api${NC}"
        exit 1
    fi
    
    # Intentar abrir en el navegador
    if command -v open &> /dev/null; then
        open "$API_URL/api/v1/docs"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$API_URL/api/v1/docs"
    else
        echo "${CYAN}[INFO] Documentación: $API_URL/api/v1/docs${NC}"
        echo "${CYAN}[INFO] ReDoc: $API_URL/api/v1/redoc${NC}"
    fi
}

# ========== PROCESAMIENTO DE ARGUMENTOS ==========

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
    "logs")
        show_logs
        ;;
    "clean")
        clean_system
        ;;
    "status")
        show_status
        ;;
    # NUEVAS OPCIONES RESTART
    "restart")
        restart_api
        ;;
    "restart-build")
        restart_api "build"
        ;;
    # API FastAPI (SOLO DOCKER)
    "api")
        start_api_docker
        ;;
    "api-prod")
        start_api_prod
        ;;
    "api-nginx")
        start_api_nginx
        ;;
    "test-api")
        test_api
        ;;
    "stop-api")
        stop_api
        ;;
    "docs")
        open_docs
        ;;
    *)
        echo "${RED}[ERROR] Opción desconocida: $1${NC}"
        show_help
        exit 1
        ;;
esac

echo ""
echo "${GREEN}[OK] Operación completada${NC}"
echo "============================================================"