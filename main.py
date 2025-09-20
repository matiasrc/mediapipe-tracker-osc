import sys
import cv2
import json
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QComboBox,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QCheckBox
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

# --- Todas las importaciones importantes van al principio para estabilidad ---
from camera_thread import CameraThread
from models.hands_model import HandsModel
from models.pose_model import PoseModel
from models.face_model import FaceModel
from models.holistic_model import HolisticModel
from osc_client import OSCClient

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"ip": "127.0.0.1", "port": 3333, "camera_index": 0, "model": "Hands"}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"[CONFIG ERROR] {e}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MediaPipe Tracker OSC")
        self.setFixedSize(960, 760)

        self.config = load_config()
        
        # --- Cargar componentes pesados desde el inicio ---
        self.osc_client = OSCClient(self.config.get("ip"), self.config.get("port"))
        self.camera_thread = CameraThread(osc_client=self.osc_client)
        self.model = None

        # ---- Vista previa (inicialmente muestra "Cargando...") ----
        self.image_label = QLabel("Iniciando, por favor espere...")
        self.image_label.setFixedSize(960, 640)
        self.image_label.setAlignment(Qt.AlignCenter)
        font = self.image_label.font()
        font.setPointSize(20)
        self.image_label.setFont(font)
        self.image_label.setStyleSheet("background-color: #333; color: #EEE;")

        # ---- Controles (creados pero no conectados aun) ----
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Hands", "Pose", "Face", "Holistic"])

        self.camera_selector = QComboBox()

        self.start_button = QPushButton("Iniciar")
        self.stop_button = QPushButton("Detener")

        self.osc_checkbox = QCheckBox("Enviar OSC")
        self.osc_checkbox.setChecked(True)

        self.ip_edit = QLineEdit(self.config.get("ip", "127.0.0.1"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.config.get("port", 3333))
        
        self.model_selector.setEnabled(False)
        self.camera_selector.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # ---- Layouts ----
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Modelo:"))
        controls_layout.addWidget(self.model_selector)
        controls_layout.addSpacing(15)
        controls_layout.addWidget(QLabel("Cámara:"))
        controls_layout.addWidget(self.camera_selector)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)

        osc_layout = QHBoxLayout()
        osc_layout.addWidget(self.osc_checkbox)
        osc_layout.addSpacing(10)
        osc_layout.addWidget(QLabel("IP:"))
        osc_layout.addWidget(self.ip_edit)
        osc_layout.addWidget(QLabel("Puerto:"))
        osc_layout.addWidget(self.port_spin)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addLayout(controls_layout)
        layout.addLayout(osc_layout)
        self.setLayout(layout)
        
        QTimer.singleShot(50, self.finish_setup)

    def finish_setup(self):
        """ Busca cámaras, conecta señales y habilita la UI. """
        self.image_label.setText("Buscando cámaras...")
        QApplication.processEvents()

        self.populate_cameras()

        self.image_label.setText("Listo para iniciar.")
        self.image_label.setStyleSheet("")
        
        # --- Cargar modelo inicial guardado ---
        model_name = self.config.get("model", "Hands")
        self.change_model(model_name)
        
        # --- CONECTAR SEÑALES AHORA QUE TODO EXISTE ---
        self.model_selector.currentTextChanged.connect(self.change_model)
        self.camera_selector.currentIndexChanged.connect(self.change_camera)
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.osc_checkbox.stateChanged.connect(self.toggle_osc)
        self.ip_edit.textChanged.connect(self.apply_osc_target)
        self.port_spin.valueChanged.connect(self.apply_osc_target)
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.enable_osc(self.osc_checkbox.isChecked())

        # --- Restaurar estado guardado ---
        self.model_selector.setCurrentText(model_name)
        cam_index = self.config.get("camera_index", 0)
        cam_idx_found = False
        for i in range(self.camera_selector.count()):
            if self.camera_selector.itemData(i) == cam_index:
                self.camera_selector.setCurrentIndex(i)
                cam_idx_found = True
                break
        if not cam_idx_found and self.camera_selector.count() > 0:
            self.camera_selector.setCurrentIndex(0)
            
        # --- Habilitar UI ---
        self.model_selector.setEnabled(True)
        self.camera_selector.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(True)

    def populate_cameras(self):
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.camera_selector.addItem(f"Cámara {i}", i)
                cap.release()
        if self.camera_selector.count() == 0:
            self.camera_selector.addItem("Sin cámaras", -1)

    def start_camera(self):
        idx = self.camera_selector.currentData()
        if idx is not None and idx >= 0:
            self.camera_thread.set_camera_index(idx)
            self.camera_thread.start()

    def stop_camera(self):
        self.camera_thread.stop()

    def change_camera(self, index):
        cam_idx = self.camera_selector.itemData(index)
        if cam_idx is not None and cam_idx >= 0:
            was_running = self.camera_thread.running
            self.camera_thread.stop()
            self.camera_thread.set_camera_index(cam_idx)
            if was_running:
                self.camera_thread.start()

            self.config["camera_index"] = cam_idx
            save_config(self.config)

    def change_model(self, name):
        if name == "Hands":
            self.model = HandsModel()
        elif name == "Pose":
            self.model = PoseModel()
        elif name == "Face":
            self.model = FaceModel()
        elif name == "Holistic":
            self.model = HolisticModel()
        
        self.camera_thread.set_model(self.model)
        self.config["model"] = name
        save_config(self.config)

    def toggle_osc(self, state):
        enabled = (state == Qt.Checked)
        self.camera_thread.enable_osc(enabled)

    def apply_osc_target(self):
        ip = self.ip_edit.text().strip()
        port = int(self.port_spin.value())
        self.osc_client.set_target(ip, port)
        self.config["ip"] = ip
        self.config["port"] = port
        save_config(self.config)

    def update_frame(self, frame_bgr):
        h, w, ch = frame_bgr.shape
        qimg = QImage(frame_bgr.data, w, h, ch * w, QImage.Format_BGR888)
        pix = QPixmap.fromImage(qimg)
        pix = pix.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pix)

    def closeEvent(self, event):
        self.camera_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

