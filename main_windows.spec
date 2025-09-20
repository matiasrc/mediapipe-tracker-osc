    # -*- mode: python ; coding: utf-8 -*-

    from PyInstaller.utils.hooks import collect_data_files

    # --- Recolectar todos los archivos de datos de MediaPipe ---
    # Esta lógica es la misma que para Mac. Se asegura de que todos los
    # modelos .tflite y .task se incluyan en la compilación.
    datas = collect_data_files('mediapipe')

    # --- Añadir tus propios archivos de modelo y configuración ---
    datas += [
        ('models', 'models'),
        ('config.json', '.')
    ]

    a = Analysis(
        ['main.py'],
        pathex=[],
        binaries=[],
        datas=datas,
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
        name='MediapipeOSC',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        # 'console=False' es clave para que no se abra una ventana de terminal negra.
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='MediapipeOSC_Windows',
    )
    ```

3.  **Ejecutar la Compilación:**
    * Abre el **Símbolo del sistema** (Command Prompt o `cmd`) en Windows.
    * Navega hasta la carpeta de tu proyecto usando el comando `cd`. Por ejemplo:
        ```bash
        cd C:\Users\TuUsuario\Desktop\mediapipe-tracker-osc
        ```
    * **Ejecuta el script `launch.bat`** que ya tienes en el proyecto. Esto creará el entorno virtual e instalará todas las dependencias necesarias.
        ```bash
        launch.bat
        ```
    * Una vez que el entorno esté activado (verás `(mediapipe-env)` al inicio de la línea), instala PyInstaller:
        ```bash
        pip install pyinstaller
        ```
    * Finalmente, ejecuta la compilación usando el nuevo archivo `.spec`:
        ```bash
        pyinstaller main_windows.spec
        
