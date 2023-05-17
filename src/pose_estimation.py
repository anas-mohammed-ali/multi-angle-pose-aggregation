# src/pose_estimation.py

import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    """
    A wrapper class for MediaPipe Pose detection.

    This class provides methods to detect human pose landmarks from images or video frames,
    draw the landmarks on the input frame, and extract keypoint coordinates.
    """
    def __init__(self, static_image_mode=False, model_complexity=1, enable_segmentation=False,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the PoseEstimator with MediaPipe Pose parameters.

        Args:
            static_image_mode (bool): Whether to treat input as static images (True) or video (False)
            model_complexity (int): Model complexity (0, 1, or 2). Higher is more accurate but slower
            enable_segmentation (bool): Whether to enable segmentation
            min_detection_confidence (float): Minimum confidence for detection to be considered successful
            min_tracking_confidence (float): Minimum confidence for pose landmarks to be tracked between frames
        """
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def detect(self, frame):
        """
        Process a frame to detect pose landmarks.

        Args:
            frame: Input image/frame in BGR format (OpenCV default)

        Returns:
            MediaPipe pose processing result
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb_frame)
        return result

    def draw_landmarks(self, frame, result, draw_style=True):
        """
        Draw detected pose landmarks on the input frame.

        Args:
            frame: Input image/frame in BGR format
            result: MediaPipe pose processing result
            draw_style (bool): Whether to use the predefined drawing styles

        Returns:
            Frame with landmarks drawn
        """
        if result.pose_landmarks:
            if draw_style:
                self.mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
            else:
                self.mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS
                )
        return frame

    def get_keypoints(self, result, frame_width, frame_height):
        """
        Extract keypoint coordinates from pose landmarks.

        Args:
            result: MediaPipe pose processing result
            frame_width: Width of the input frame
            frame_height: Height of the input frame

        Returns:
            List of tuples (x, y, z, visibility) for each landmark, or None if no pose detected
        """
        if not result.pose_landmarks:
            return None

        keypoints = []
        for lm in result.pose_landmarks.landmark:
            x = int(lm.x * frame_width)
            y = int(lm.y * frame_height)
            z = lm.z  # Depth relative to hips
            visibility = lm.visibility
            keypoints.append((x, y, z, visibility))
        return keypoints

    def get_pose_angles(self, keypoints):
        """
        Calculate joint angles from keypoints.

        Args:
            keypoints: List of keypoint tuples (x, y, z, visibility)

        Returns:
            Dictionary of joint angles in degrees
        """
        if not keypoints or len(keypoints) < 33:  # MediaPipe has 33 pose landmarks
            return {}

        # Extract key points for angle calculations
        # Example: Calculate elbow angle
        def calculate_angle(a, b, c):
            a = np.array([a[0], a[1]])  # First point
            b = np.array([b[0], b[1]])  # Mid point (joint)
            c = np.array([c[0], c[1]])  # End point

            # Calculate vectors
            ba = a - b
            bc = c - b

            # Calculate angle using dot product
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(cosine_angle)

            return np.degrees(angle)

        # Calculate right elbow angle (shoulder, elbow, wrist)
        right_elbow_angle = calculate_angle(
            keypoints[11][:2],  # Right shoulder
            keypoints[13][:2],  # Right elbow
            keypoints[15][:2]   # Right wrist
        )

        # Calculate left elbow angle
        left_elbow_angle = calculate_angle(
            keypoints[12][:2],  # Left shoulder
            keypoints[14][:2],  # Left elbow
            keypoints[16][:2]   # Left wrist
        )

        return {
            "right_elbow": right_elbow_angle,
            "left_elbow": left_elbow_angle
        }
# Enhanced pose estimation
