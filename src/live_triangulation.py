# src/live_triangulation.py

import sys
import os

# Add utils/ to import path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UTILS_PATH = os.path.join(PROJECT_ROOT, "..", "utils")
sys.path.append(UTILS_PATH)

import cv2
import numpy as np
from pose_estimation import PoseEstimator
from triangulate_3d_pose import triangulate_point


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    estimator1 = PoseEstimator()
    estimator2 = PoseEstimator()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Stereo intrinsics
    focal_length = frame_width
    cx, cy = frame_width // 2, frame_height // 2
    baseline = 10.0  # cm

    cam_matrix1 = np.array([[focal_length, 0, cx, 0],
                            [0, focal_length, cy, 0],
                            [0, 0, 1, 0]])

    cam_matrix2 = np.array([[focal_length, 0, cx, -focal_length * baseline],
                            [0, focal_length, cy, 0],
                            [0, 0, 1, 0]])

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break

        flipped = cv2.flip(frame, 1)

        h, w, _ = frame.shape
        result1 = estimator1.detect(frame)
        result2 = estimator2.detect(flipped)

        kp1 = estimator1.get_keypoints(result1, w, h)
        kp2 = estimator2.get_keypoints(result2, w, h)

        overlay = frame.copy()
        overlay = estimator1.draw_landmarks(overlay, result1)

        if kp1 and kp2:
            for i in range(min(len(kp1), len(kp2))):
                x1, y1, *_ = kp1[i]
                x2, y2, *_ = kp2[i]

                p1 = np.array([x1, y1])
                p2 = np.array([x2, y2])

                point_3d = triangulate_point(p1, p2, cam_matrix1, cam_matrix2)

                # Show 3D coordinate overlay near joint
                text = f"{i}: ({point_3d[0]:.1f}, {point_3d[1]:.1f}, {point_3d[2]:.1f})"
                cv2.putText(overlay, text, (x1 + 5, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("Live Pose with 3D Coordinates (Press Q to Quit)", overlay)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
