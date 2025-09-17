import sys
import cv2
import json
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QComboBox,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QCheckBox
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

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

        self.setWindowTitle("MediaPipe tracker OSC")
        self.setFixedSize(960, 760)

        self.config = load_config()

        # ---- Preview ----
        self.image_label = QLabel()
        self.image_label.setFixedSize(960, 640)
        self.image_label.setAlignment(Qt.AlignCenter)

        # ---- Model selector ----
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Hands", "Pose", "Face", "Holistic"])
        self.model_selector.currentTextChanged.connect(self.change_model)

        # ---- Camera selector ----
        self.camera_selector = QComboBox()
        self.populate_cameras()
        self.camera_selector.currentIndexChanged.connect(self.change_camera)

        # ---- Start/Stop camera ----
        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button = QPushButton("Detener")
        self.stop_button.clicked.connect(self.stop_camera)

        # ---- OSC controls ----
        self.osc_checkbox = QCheckBox("Enviar OSC")
        self.osc_checkbox.stateChanged.connect(self.toggle_osc)

        self.ip_edit = QLineEdit()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)

        # Set initial values after widgets are created
        self.ip_edit.setText(self.config.get("ip", "127.0.0.1"))
        self.port_spin.setValue(self.config.get("port", 3333))

        # Connect IP and port changes to apply_osc_target
        self.ip_edit.textChanged.connect(self.apply_osc_target)
        self.port_spin.valueChanged.connect(self.apply_osc_target)

        # ---- Thread & Model & OSC ----
        self.osc_client = OSCClient(self.ip_edit.text(), self.port_spin.value())
        self.camera_thread = CameraThread(osc_client=self.osc_client)

        # Habilitar OSC por defecto y guardar en configuración
        self.osc_checkbox.setChecked(True)
        self.config["ip"] = self.ip_edit.text().strip()
        self.config["port"] = int(self.port_spin.value())
        save_config(self.config)

        # Instantiate model according to current config
        model_name = self.config.get("model", "Hands")
        if model_name == "Hands":
            self.model = HandsModel()
        elif model_name == "Pose":
            self.model = PoseModel()
        elif model_name == "Face":
            self.model = FaceModel()
        elif model_name == "Holistic":
            self.model = HolisticModel()
        else:
            self.model = HandsModel()
        self.camera_thread.set_model(self.model)

        self.camera_thread.frame_ready.connect(self.update_frame)

        # Set model selector current text
        self.model_selector.setCurrentText(model_name)

        # Set camera index selection if available
        cam_index = self.config.get("camera_index", 0)
        cam_idx_found = False
        for i in range(self.camera_selector.count()):
            if self.camera_selector.itemData(i) == cam_index:
                self.camera_selector.setCurrentIndex(i)
                cam_idx_found = True
                break
        if not cam_idx_found and self.camera_selector.count() > 0:
            self.camera_selector.setCurrentIndex(0)

        # Layouts superiores
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

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addLayout(controls_layout)
        layout.addLayout(osc_layout)
        self.setLayout(layout)

    # ---------- UI handlers ----------
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
            self.camera_thread.set_camera_index(cam_idx)
            self.config["camera_index"] = cam_idx
            save_config(self.config)

    def change_model(self, name):
        # Instantiate the correct model class
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
        self.camera_thread.set_osc_client(self.osc_client)
        self.config["ip"] = ip
        self.config["port"] = port
        save_config(self.config)

    def update_frame(self, frame_bgr):
        h, w, ch = frame_bgr.shape
        qimg = QImage(frame_bgr.data, w, h, ch * w, QImage.Format_BGR888)
        # Scale with aspect ratio to fit the label
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