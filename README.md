# **MediaPipe Tracker OSC**

Esta es una aplicación de escritorio para Mac y Windows que utiliza la librería MediaPipe de Google para realizar seguimiento corporal, facial y de manos en tiempo real a través de una cámara web. Los datos de los puntos detectados (landmarks) se envían a través del protocolo OSC, permitiendo una fácil integración con entornos creativos como Processing, TouchDesigner, VVVV, Unity, etc.  
**Autores y Aclaración Importante**

* Este software fue desarrollado por **Matías Romero Costas** en colaboración con **Daniel Loaiza**.  
* Por favor, ten en cuenta que este es un proyecto experimental. Se distribuye "tal cual", sin garantías de ningún tipo, explícitas o implícitas. No se ofrece soporte técnico. El uso de esta aplicación es de exclusiva responsabilidad del usuario.

## **Características**

* **Seguimiento Multimodelo:** Soporta los modelos Hands, Pose, Face y Holistic de MediaPipe.  
* **Envío por OSC:** Transmite los datos de los landmarks en un formato simple y fácil de parsear.  
* **Interfaz Gráfica Sencilla:** Permite seleccionar el modelo, la cámara y configurar el destino OSC (IP y puerto) fácilmente.  
* **Multiplataforma:** Compilado para funcionar como una aplicación nativa en macOS y Windows sin necesidad de instalar dependencias.

## **¿Cómo Usar la Aplicación? (Para Usuarios Finales)**

No necesitas instalar Python ni ninguna librería para usar esta aplicación.

1. **Descarga la Versión para tu Sistema Operativo:**  
   * Ve a la sección de [**Releases**](https://www.google.com/search?q=https://github.com/matiasrc/mediapipe-tracker-osc/releases) en este repositorio.  
   * Descarga el archivo .zip para macOS o Windows.  
2. **Descomprime y Ejecuta:**  
   * **En macOS:** Descomprime el archivo y encontrarás MediapipeOSC.app. Haz doble clic para ejecutarla. (Es posible que la primera vez necesites hacer clic derecho \> Abrir).  
   * **En Windows:** Descomprime el archivo y encontrarás una carpeta. Dentro, ejecuta MediapipeOSC.exe.  
3. **Configura y Empieza a Rastrear:**  
   * Selecciona el **Modelo** que deseas utilizar.  
   * Elige la **Cámara** que quieres que use la aplicación.  
   * Configura la **IP** y el **Puerto** del programa que recibirá los datos OSC.  
   * Presiona **Iniciar**.

## **Formato de los Mensajes OSC**

La aplicación envía los datos en un formato de array (lista de floats) para mayor eficiencia. Cada mensaje comienza con una cabecera de 4 valores que describe el contenido.

#### **Cabecera (Común a todos los mensajes)**

* address: /faces/arr, /hands/arr o /poses/arr  
* payload\[0\]: (int) Ancho del fotograma de la cámara.  
* payload\[1\]: (int) Alto del fotograma de la cámara.  
* payload\[2\]: (int) Número de instancias detectadas (caras, manos, etc.).  
* payload\[3\]: (float) Puntuación general de la detección (actualmente siempre 1.0).

#### **Datos por Landmark (Punto)**

Después de la cabecera, los datos de cada landmark se envían en grupos de **3 valores**:

* x: (float) Coordenada X normalizada (0.0 a 1.0).  
* y: (float) Coordenada Y normalizada (0.0 a 1.0).  
* score: (float) Puntuación de confianza o visibilidad del punto (0.0 a 1.0).

#### **Estructura del Payload por Modelo**

| Modelo | Dirección OSC | Puntos por instancia | Valores por instancia | Total de valores (1 instancia) |
| :---- | :---- | :---- | :---- | :---- |
| **Face** | /faces/arr | 468 | 1404 (468 x 3\) | 1408 (1404 \+ cabecera) |
| **Hands** | /hands/arr | 21 | 63 (21 x 3\) | 67 (63 \+ cabecera) |
| **Pose** | /poses/arr | 17 | 51 (17 x 3\) | 55 (51 \+ cabecera) |

Ejemplo para Manos (/hands/arr):  
Si se detectan 2 manos, el payload se vería así:  
\[ancho, alto, 2, 1.0, x1,y1,score1 ... (21 puntos mano 1), x1,y1,score1 ... (21 puntos mano 2)\]

## **Solución de Problemas (Errores Comunes)**

* **La aplicación no se abre en macOS:**  
  * Si al hacer doble clic te aparece un error de seguridad, haz **clic derecho** sobre MediapipeOSC.app y selecciona **Abrir**. Esto te permitirá autorizar la ejecución.  
* **La aplicación se cierra inesperadamente al iniciar (macOS):**  
  * La aplicación necesita permiso para acceder a la cámara. Ve a **Preferencias del Sistema \> Privacidad y Seguridad \> Cámara** y asegúrate de que MediapipeOSC (o tu Terminal, si ejecutas desde el código) tenga el permiso activado.  
* **No se reciben datos en el programa receptor (Processing, TouchDesigner, etc.):**  
  * Verifica que la **IP** y el **Puerto** en la aplicación coincidan exactamente con la IP y el puerto de escucha en tu programa receptor.  
  * Si usas la IP 127.0.0.1, ambos programas deben estar en el mismo ordenador.  
  * Asegúrate de que ningún **firewall** (de Windows o macOS) esté bloqueando la conexión.

## **Para Desarrolladores (Compilar desde el Código Fuente)**

Si quieres modificar el código, necesitarás Python 3.10 y las dependencias del proyecto.

1. **Clona el Repositorio:**  
   git clone \[https://github.com/matiasrc/mediapipe-tracker-osc.git\](https://github.com/matiasrc/mediapipe-tracker-osc.git)  
   cd mediapipe-tracker-osc

2. Ejecuta el Script de Inicio:  
   El script creará un entorno virtual e instalará las dependencias.  
   * En macOS: sh launch.sh  
   * En Windows: launch.bat

### **Compilar la Aplicación**

Para crear los ejecutables autocontenidos, necesitarás pyinstaller.

1. **Activa el Entorno Virtual** e instala PyInstaller:  
   pip install pyinstaller

2. **Ejecuta el Compilador:**  
   * **Para macOS:** Usa el archivo main.spec para crear el paquete .app.  
     pyinstaller main.spec

   * **Para Windows:** Usa el archivo main\_windows.spec.  
     pyinstaller main\_windows.spec

3. **Encuentra el Ejecutable:**  
   * La aplicación final estará en la carpeta dist/.