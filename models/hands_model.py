import cv2
import mediapipe as mp

class HandsModel:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.drawer = mp.solutions.drawing_utils
        self.hand_connections = self.mp_hands.HAND_CONNECTIONS
        self._last_hands = []

    def process(self, rgb_image):
        h, w = rgb_image.shape[:2]
        results = self.hands.process(rgb_image)
        self._last_hands = []

        overlay = rgb_image.copy()
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                pts = []
                for lm in hand_lms.landmark:
                    score = 1.0  # MediaPipe Hands no tiene score por punto
                    pts.append((lm.x, lm.y, score))
                self._last_hands.append(pts)

                # Puntos azules + líneas blancas
                self.drawer.draw_landmarks(
                    overlay,
                    hand_lms,
                    self.hand_connections,
                    self.drawer.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.drawer.DrawingSpec(color=(255, 255, 255), thickness=2)
                )

        return overlay

    # Ejemplo para pose_model.py
    def get_osc_packets(self, frame_w, frame_h):
        # print(f"[DEBUG] _last_hands: {self._last_hands}")
        n = len(self._last_hands)
        if n == 0:
            return []
        payload = [int(frame_w), int(frame_h), int(n)]
        for pts in self._last_hands:
            payload.append(float(1.0))
            for (nx, ny, score) in pts:
                x = float(nx) if nx is not None else 0.0
                y = float(ny) if ny is not None else 0.0    
                score = float(score) if score is not None else 0.0
                payload.extend([x, y, score])
        return [("/hands/arr", payload)]