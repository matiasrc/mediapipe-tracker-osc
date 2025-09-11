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

## 📡 Datos enviados por OSC

### Hands

* **Landmarks:** 21 por mano.
* **Datos por landmark:** `x (float), y (float), z (float), score (float)`
* **Total por mano:** 84 valores (`21 × 4`).

### Pose

* **Landmarks:** 33.
* **Datos por landmark:** `x (float), y (float), z (float), score (float)`
* **Total:** 132 valores (`33 × 4`).

### Face

* **Landmarks:** 468.
* **Datos por landmark:** `x (float), y (float), score (float)`
* **Total:** 1404 valores (`468 × 3`).

---

## 📑 Formato del Payload OSC

Orden de los datos enviados:

1. `frame_w (int)`
2. `frame_h (int)`
3. `num_faces / num_hands / num_pose` (int)
4. `1.0` por cada objeto detectado (placeholder, float)
5. Para cada landmark:

   * `x (float)`
   * `y (float)`
   * `z (float)` (solo en manos y pose)
   * `score (float)`

Ejemplo de mensaje OSC para **manos**:

```
/hands/arr [640, 480, 1, 1.0, x1, y1, z1, score1, x2, y2, z2, score2, ...]
```

---

## 🛠️ Troubleshooting (Errores comunes)

### 1. Error: `ModuleNotFoundError: No module named 'pythonosc'`

➡ Solución: Ejecutar manualmente:

```bash
pip install python-osc
```

### 2. Error en Windows: `ImportError: DLL load failed while importing _framework_bindings`

➡ Esto ocurre si se usa Python 3.11 o superior.
**Solución:** Instalar Python **3.10.x** y volver a ejecutar `launch.bat`.

### 3. Error: `Permission denied` al ejecutar `launch.sh` en macOS

➡ El script no tiene permisos de ejecución.
**Solución:**

```bash
chmod +x launch.sh
```

### 4. Error: La cámara no se inicializa (`camera failed to properly initialize`)

➡ Puede ocurrir si hay múltiples cámaras.
**Solución:** Editar el código en `camera_thread.py` y probar con otro índice de cámara (`cv2.VideoCapture(0)` → `cv2.VideoCapture(1)`).

---

## 📝 Notas

* **No es necesario instalar nada más** aparte de Python 3.10.
* Si ya tenías otra versión de Python instalada, **no hay problema** siempre y cuando también tengas Python 3.10.
* La primera ejecución puede tardar porque instala librerías, luego abrirá mucho más rápido.
