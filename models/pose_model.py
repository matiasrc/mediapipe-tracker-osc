import cv2
import mediapipe as mp

# Mapa de índices MediaPipe Pose (33) → orden PoseNet (17)
# PoseNet: [nose, lEye, rEye, lEar, rEar, lSh, rSh, lElb, rElb, lWr, rWr, lHip, rHip, lKnee, rKnee, lAnk, rAnk]
POSENET_FROM_MEDIAPIPE = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]

class PoseModel:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.drawer = mp.solutions.drawing_utils
        self.pose_connections = self.mp_pose.POSE_CONNECTIONS
        self._last_poses = []

    def process(self, rgb_image):
        h, w = rgb_image.shape[:2]
        results = self.pose.process(rgb_image)
        self._last_poses = []

        overlay = rgb_image.copy()
        if results.pose_landmarks:
            pts = []
            for lm in results.pose_landmarks.landmark:
                score = lm.visibility if hasattr(lm, "visibility") else 1.0
                pts.append((lm.x, lm.y, score))
            self._last_poses.append(pts)

            # Puntos azules + líneas blancas
            self.drawer.draw_landmarks(
                overlay,
                results.pose_landmarks,
                self.pose_connections,
                self.drawer.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.drawer.DrawingSpec(color=(255, 255, 255), thickness=2)
            )
        return overlay

    def get_osc_packets(self, frame_w, frame_h):
        # Usar SOLO 17 puntos en orden PoseNet
        n = len(self._last_poses)
        if n == 0:
            return []
        payload = [int(frame_w), int(frame_h), int(n)]
        for pts33 in self._last_poses:
            # score por pose:
            payload.append(1.0)
            # mapear 33 → 17
            for mi in POSENET_FROM_MEDIAPIPE:
                nx, ny, score = pts33[mi]
                x = float(nx) if nx is not None else 0.0
                y = float(ny) if ny is not None else 0.0        
                s = float(score) if score is not None else 0.0
                payload.extend([x, y, s])
        return [("/poses/arr", payload)]