# ──────────────────────────────
# OCR-CLI   (Python 3.8 slim)
# ──────────────────────────────
FROM python:3.8-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/

# Crear directorios necesarios
RUN mkdir -p resultado temp pdfs

# Usuario no root para seguridad
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Configurar PYTHONPATH
ENV PYTHONPATH=/app/src

# Comando por defecto - menú interactivo
CMD ["python", "-m", "interfaces.cli.interactive_menu"]