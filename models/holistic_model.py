import cv2
import mediapipe as mp

# Mapa de índices MediaPipe Pose (33) → orden PoseNet (17)
# PoseNet: [nose, lEye, rEye, lEar, rEar, lSh, rSh, lElb, rElb, lWr, rWr, lHip, rHip, lKnee, rKnee, lAnk, rAnk]
POSENET_FROM_MEDIAPIPE = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

class HolisticModel:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            refine_face_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.drawer = mp.solutions.drawing_utils
        self._last_data = {}

    def process(self, rgb_image):
        results = self.holistic.process(rgb_image)
        self._last_data = {}
        h, w = rgb_image.shape[:2]
        overlay = rgb_image.copy()

        # Pose
        if results.pose_landmarks:
            pts = []
            for lm in results.pose_landmarks.landmark:
                score = lm.visibility if hasattr(lm, "visibility") else 1.0
                pts.append((lm.x, lm.y, score))
            self._last_data["pose"] = pts
            self.drawer.draw_landmarks(
                overlay,
                results.pose_landmarks,
                self.mp_holistic.POSE_CONNECTIONS,
                self.drawer.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.drawer.DrawingSpec(color=(255, 255, 255), thickness=2)
            )

        # Manos
        for hand_name, hand_landmarks in [("left_hand", results.left_hand_landmarks), ("right_hand", results.right_hand_landmarks)]:
            if hand_landmarks:
                pts = []
                for lm in hand_landmarks.landmark:
                    score = lm.visibility if hasattr(lm, "visibility") else 1.0
                    pts.append((lm.x, lm.y, score))
                self._last_data[hand_name] = pts
                self.drawer.draw_landmarks(
                    overlay,
                    hand_landmarks,
                    self.mp_holistic.HAND_CONNECTIONS,
                    self.drawer.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.drawer.DrawingSpec(color=(255, 255, 255), thickness=2)
                )

        # Cara (usar los 468 puntos completos)
        if results.face_landmarks:
            pts = []
            for lm in results.face_landmarks.landmark:
                score = lm.visibility if hasattr(lm, "visibility") else 1.0
                pts.append((lm.x, lm.y, score))
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(overlay, (cx, cy), 1, (0, 255, 0), -1)
            self._last_data["face"] = pts
            print(f"Face landmarks count: {len(pts)}")  # Debug print for face landmarks count

        return overlay

    def get_osc_packets(self, frame_w, frame_h):
        packets = []

        # --- POSE (17 puntos PoseNet) ---
        if "pose" in self._last_data and len(self._last_data["pose"]) >= 33:
            pts33 = self._last_data["pose"]
            payload = [int(frame_w), int(frame_h), 1]  # siempre 1 pose como máximo
            payload.append(1.0)  # score por pose
            for mi in POSENET_FROM_MEDIAPIPE:
                nx, ny, score = pts33[mi]
                x = float(nx * frame_w) if nx is not None else 0.0
                y = float(ny * frame_h) if ny is not None else 0.0
                s = float(score) if score is not None else 0.0
                payload.extend([x, y, s])
            packets.append(("/poses/arr", payload))

        # --- HANDS (combinar ambas manos en 1 mensaje) ---
        hands_list = []
        for hand_key in ["left_hand", "right_hand"]:
            if hand_key in self._last_data and len(self._last_data[hand_key]) == 21:
                hands_list.append(self._last_data[hand_key])

        if len(hands_list) > 0:
            payload = [int(frame_w), int(frame_h), int(len(hands_list))]
            for pts in hands_list:
                payload.append(1.0)  # score por mano
                for (nx, ny, score) in pts:
                    x = float(nx * frame_w) if nx is not None else 0.0
                    y = float(ny * frame_h) if ny is not None else 0.0
                    s = float(score) if score is not None else 0.0
                    payload.extend([x, y, s])
            packets.append(("/hands/arr", payload))

        # --- FACE (468 puntos completos) ---
        if "face" in self._last_data and len(self._last_data["face"]) == 468:
            pts = self._last_data["face"]
            payload = [int(frame_w), int(frame_h), 1]
            payload.append(1.0)  # score por cara
            for (nx, ny, score) in pts:
                x = float(nx * frame_w) if nx is not None else 0.0
                y = float(ny * frame_h) if ny is not None else 0.0
                s = float(score) if score is not None else 0.0
                payload.extend([x, y, s])
            packets.append(("/faces/arr", payload))

        return packets