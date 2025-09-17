import os
import cv2
import mediapipe as mp

class FaceModel:
    def __init__(self, max_num_faces=5, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            refine_landmarks=True,
            max_num_faces=max_num_faces,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self._last_faces = []
        self._frame_counter = 0

    def process(self, rgb_image):
        h, w = rgb_image.shape[:2]
        results = self.mesh.process(rgb_image)
        self._last_faces = []

        overlay = rgb_image.copy()
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                pts = []
                for lm in face_landmarks.landmark:
                    score = getattr(lm, "presence", None)
                    if score is None:
                        score = getattr(lm, "visibility", 1.0)
                    pts.append((lm.x, lm.y, score))
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(overlay, (cx, cy), 2, (0, 255, 0), -1)
                self._last_faces.append(pts)

        return overlay

    def get_osc_packets(self, frame_w, frame_h):
        packets = []
        
        # Se filtran las caras para asegurar que tengan al menos 468 puntos
        valid_faces = [pts for pts in self._last_faces if len(pts) >= 468]
        n = len(valid_faces)

        if n > 0:
            payload = [int(frame_w), int(frame_h), int(n)]
            for pts in valid_faces:
                payload.append(float(1.0)) # score por cara
                # Se itera solo hasta 468 para asegurar un tamaño de paquete consistente
                for i in range(468):
                    nx, ny, score = pts[i]
                    x = float(nx) if nx is not None else 0.0
                    y = float(ny) if ny is not None else 0.0
                    score = float(score) if score is not None else 0.0
                    payload.extend([x, y, score])
            if len(payload) > 3: # Solo enviar si se añadieron datos de caras
                packets.append(("/faces/arr", payload))

        return packets

