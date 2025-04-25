# src/pose_estimation.py

import cv2
import mediapipe as mp

class PoseEstimator:
    def __init__(self, static_image_mode=False, model_complexity=1, enable_segmentation=False):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            enable_segmentation=enable_segmentation
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb_frame)
        return result

    def draw_landmarks(self, frame, result):
        if result.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                result.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        return frame

    def get_keypoints(self, result, frame_width, frame_height):
        if not result.pose_landmarks:
            return None

        keypoints = []
        for lm in result.pose_landmarks.landmark:
            x = int(lm.x * frame_width)
            y = int(lm.y * frame_height)
            z = lm.z  # Depth relative to hips; we might use this later
            visibility = lm.visibility
            keypoints.append((x, y, z, visibility))
        return keypoints
