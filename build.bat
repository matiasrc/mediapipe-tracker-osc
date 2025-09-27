@echo off

IF NOT EXIST mediapipe-env (
    echo Creando entorno virtual: mediapipe-env...
    python -m venv mediapipe-env
)

call "mediapipe-env\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install python-osc
pip install opencv-python mediapipe PyQt5
pip install pyinstaller

pyinstaller main_windows.spec

echo La aplicacion ha terminado.
pause


