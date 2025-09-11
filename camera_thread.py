import cv2
import threading
from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np

class CameraThread(QObject):
    frame_ready = pyqtSignal(np.ndarray)

    def __init__(self, osc_client=None):
        super().__init__()
        self.cap = None
        self.running = False
        self.model = None  # modelo actual (pose, hands, etc.)
        self.thread = None
        self.osc_client = osc_client
        self.osc_enabled = osc_client is not None

    def set_model(self, model):
        self.model = model

    def set_osc_client(self, osc_client):
        self.osc_client = osc_client

    def enable_osc(self, enabled: bool):
        self.osc_enabled = bool(enabled)

    def start(self, camera_index=0):
        if self.running:
            return
        self.running = True
        self.cap = cv2.VideoCapture(camera_index)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def set_camera_index(self, index):
        self.stop()
        self.start(index)

    def _run(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            # BGR → RGB para MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.model:
                processed_rgb = self.model.process(rgb)
                if processed_rgb is None:
                    continue
                # Enviar OSC si corresponde
                if self.osc_enabled and self.osc_client and hasattr(self.model, "get_osc_packets"):
                    try:
                        h, w = frame.shape[:2]
                        packets = self.model.get_osc_packets(w, h)
                        if packets:  # solo enviar si hay detecciones
                            for address, payload in packets:
                                self.osc_client.send(address, payload)
                    except Exception as e:
                        print(f"[OSC ERROR] {e}")

                # RGB → BGR para mostrar en Qt
                frame = cv2.cvtColor(processed_rgb, cv2.COLOR_RGB2BGR)
            else:
                frame = cv2.putText(frame, "Sin modelo", (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            self.frame_ready.emit(frame)