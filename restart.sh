#!/bin/bash

# Script para reiniciar los contenedores después de realizar cambios

# Crear directorios necesarios
echo "Creando directorios necesarios..."
mkdir -p pdfs resultado

echo "Limpieza de sistema..."
docker system prune --all --volumes --force

echo "Reconstruyendo imágenes..."
docker compose build

echo "Iniciando contenedores..."
docker compose up --detach

echo "Esperando a que los contenedores estén listos..."
sleep 5

echo "Estado de los contenedores:"
docker ps -a | grep ocr-backend

echo "Iniciando modo interactivo..."
docker compose exec -T ocr-backend python src/interfaces/cli/main.py

