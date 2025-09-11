#!/bin/bash
# Ir a la carpeta donde está este script
cd "$(dirname "$0")"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Ejecutar la app desde la carpeta actual
python main.py