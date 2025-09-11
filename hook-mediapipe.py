from PyInstaller.utils.hooks import collect_data_files

# Incluir todos los modelos internos de MediaPipe
datas = collect_data_files('mediapipe')