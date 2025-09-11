# Mediapipe Tracker OSC

Aplicación para el seguimiento de cara, manos y cuerpo con **Mediapipe**, enviando datos vía **OSC** para usar en otros programas (ej. Pure Data, TouchDesigner, Max/MSP).

---

## 🚀 Requisitos previos

* **Python 3.10**

  * **Mac**: [Descargar aquí](https://www.python.org/ftp/python/3.10.10/python-3.10.10-macos11.pkg)
  * **Windows**: [Descargar aquí](https://www.python.org/ftp/python/3.10.10/python-3.10.10-amd64.exe)

⚠️ En Windows, durante la instalación marcar la opción **"Add Python to PATH"**.

* Una **cámara web** conectada al equipo.

---

## 💻 Cómo usar

### En **Mac**

1. Descargar la carpeta completa `mediapipe-tracker-osc`.
2. Dar permisos de ejecución al script (solo la primera vez):

   ```bash
   chmod +x launch.sh
   ```
3. Hacer doble click en `launch.sh`.
4. La primera vez puede tardar un poco porque instala dependencias.
5. Se abrirá la aplicación.

---

### En **Windows**

1. Descargar la carpeta completa `mediapipe-tracker-osc`.
2. Hacer doble click en `launch.bat`.
3. La primera vez puede tardar unos minutos porque instala dependencias.
4. Se abrirá la aplicación.

---

## 📦 Detalles técnicos

* El script crea automáticamente un entorno virtual (`mediapipe-env`) en tu usuario.
* Instala todas las dependencias necesarias (`mediapipe`, `opencv`, `python-osc`, etc.).
* Cada vez que quieras abrir la app, solo tenés que hacer doble click en `launch.sh` (Mac) o `launch.bat` (Windows).

---

## 📝 Notas

* **No es necesario instalar nada más** aparte de Python 3.10.
* Si ya tenías otra versión de Python instalada, **no hay problema** siempre y cuando también tengas Python 3.10.
* La primera ejecución puede tardar porque instala librerías, luego abrirá mucho más rápido.
