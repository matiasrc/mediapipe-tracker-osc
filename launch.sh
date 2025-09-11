#!/bin/bash

# -----------------------------
# launch.sh - Ejecuta la app y asegura dependencias
# -----------------------------

# Ruta al entorno virtual
VENV="$HOME/mediapipe-env"

# Crear entorno virtual si no existe
if [ ! -d "$VENV" ]; then
    echo "Creando entorno virtual en $VENV..."
    python3.10 -m venv "$VENV"
fi

# Activar el entorno virtual
if [ -f "$VENV/bin/activate" ]; then
    source "$VENV/bin/activate"
else
    echo "Error: No se pudo activar el entorno virtual en $VENV"
    exit 1
fi

# Navegar a la carpeta del script
cd "$(dirname "$0")" || exit

# Instalar dependencias si no están instaladas
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar la app
python main.py

# Mensaje al cerrar
echo "La aplicación ha terminado."