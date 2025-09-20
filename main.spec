# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

# --- Recolectar todos los archivos de datos de MediaPipe ---
# Esta es la parte clave. Le dice a PyInstaller que busque en la biblioteca
# de mediapipe y empaquete todos los archivos que no son de Python
# (como los modelos .tflite y .task).
datas = collect_data_files('mediapipe')

# --- Añadir tus propios archivos de modelo y configuración ---
# También nos aseguramos de que tus archivos locales se incluyan.
datas += [
    ('models', 'models'),
    ('config.json', '.')
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,  # Usamos la lista de datos que creamos arriba
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MediapipeOSC',  # Nombre del ejecutable interno
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False para crear una aplicación de ventana, no de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# --- Agrupa todos los archivos en una carpeta ---
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MediapipeOSCApp',
)

# --- Empaqueta la carpeta en una aplicación .app para macOS ---
# Esta es la sección que he restaurado.
app = BUNDLE(
    coll,
    name='MediapipeOSC.app', # El nombre final de tu aplicación
    icon=None, # Puedes añadir la ruta a un archivo .icns si tienes un icono
    bundle_identifier=None,
    info_plist={
        'NSCameraUsageDescription': 'Esta aplicación necesita acceso a tu cámara para detectar los puntos de cara, manos y cuerpo y enviarlos por OSC.'
    }
)

