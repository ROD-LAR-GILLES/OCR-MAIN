# OCR Processing API - Backend

Backend API para procesamiento de documentos OCR utilizando FastAPI y Tesseract.

## Estructura del Proyecto

```
backend/
├── src/
│   ├── application/     # Casos de uso
│   ├── domain/         # Modelos y lógica de negocio
│   ├── infrastructure/ # Adaptadores e implementaciones
│   └── interfaces/     # API REST y CLI
├── Dockerfile
├── requirements.txt
└── README.md
```

## Tecnologías

- **Python 3.11**
- **FastAPI** - Framework web
- **Tesseract OCR** - Motor de reconocimiento óptico
- **Pydantic** - Validación de datos
- **Dependency Injection** - Gestión de dependencias

## API Endpoints

- `GET /api/v1/health/` - Health check
- `POST /api/v1/files/upload` - Subir PDF
- `POST /api/v1/files/{id}/process` - Procesar documento
- `DELETE /api/v1/files/{id}` - Eliminar archivo

## Desarrollo

```bash
# Construir y ejecutar
docker-compose up --build

# Acceder a la API
curl http://localhost:8000/api/v1/health/
```

## Clean Architecture

El proyecto sigue los principios de Clean Architecture:

1. **Domain** - Lógica de negocio pura
2. **Application** - Casos de uso
3. **Infrastructure** - Implementaciones técnicas
4. **Interfaces** - Puntos de entrada (API, CLI)