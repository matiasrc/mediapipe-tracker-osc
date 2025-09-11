@echo off
SET VENV=%USERPROFILE%\mediapipe-env

IF NOT EXIST "%VENV%" (
    echo Creando entorno virtual en %VENV%...
    python -m venv "%VENV%"
)

call "%VENV%\Scripts\activate.bat"

echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
pip install python-osc

python main.py

echo La aplicacion ha terminado.
pause@echo off
SET VENV=%USERPROFILE%\mediapipe-env

IF NOT EXIST "%VENV%" (
    echo Creando entorno virtual en %VENV%...
    python -m venv "%VENV%"
)

call "%VENV%\Scripts\activate.bat"

echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
pip install python-osc

python main.py

echo La aplicacion ha terminado.
pause