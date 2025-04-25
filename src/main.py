# src/main.py

import cv2
import json
import os
from datetime import datetime
from pose_estimation import PoseEstimator

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    estimator = PoseEstimator()

    # Define project-root-relative output path
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = os.path.join(PROJECT_ROOT, "..", "assets", "keypoints")
    os.makedirs(ASSET_DIR, exist_ok=True)

    session_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(ASSET_DIR, f"pose_data_{session_time}.json")
    pose_log = []

    print(f"📦 Saving session keypoints to: {output_file}")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        height, width, _ = frame.shape

        result = estimator.detect(frame)
        frame = estimator.draw_landmarks(frame, result)

        keypoints = estimator.get_keypoints(result, width, height)
        if keypoints:
            print("🟢 Keypoints Detected:")
            keypoint_dict = {
                f"joint_{i}": {"x": x, "y": y, "z": z, "vis": vis}
                for i, (x, y, z, vis) in enumerate(keypoints)
            }
            pose_log.append(keypoint_dict)

            for i, kp in keypoint_dict.items():
                print(f"  {i}: x={kp['x']:>4}, y={kp['y']:>4}, vis={kp['vis']:.2f}")

        cv2.imshow('Pose Estimation - Press Q to Quit', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Save keypoints log to JSON
    with open(output_file, 'w') as f:
        json.dump(pose_log, f, indent=2)
    print(f"✅ Pose data saved to: {output_file}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
