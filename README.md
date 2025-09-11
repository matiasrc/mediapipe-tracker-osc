navegar hasta la carpeta del proyecto

---> cd nombreDeLaCarpeta

1. Eliminar el entorno virtual actual (si no lo estás usando para otra cosa)
rm -rf ~/mediapipe-env

2. Crear uno nuevo usando Python 3.10.10
python3.10 --version

!Si responde Python 3.10.10, entonces creamos el nuevo entorno:

python3.10 -m venv ~/mediapipe-env

3. Activar el entorno
source ~/mediapipe-env/bin/activate

4. Verificá la versión de Python en el entorno

python --version

!Debe decir: Python 3.10.10

5. Instalá las dependencias

pip install -r requirements.txt

6. Instalá osc

pip install python-osc

7. Ejecutá el programa

python main.py
