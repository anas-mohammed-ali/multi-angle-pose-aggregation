# src/main.py

import cv2
import json
import os
import argparse
import time
from datetime import datetime
from pose_estimation import PoseEstimator

def parse_arguments():
    """Parse command line arguments for the application."""
    parser = argparse.ArgumentParser(description='Real-time pose estimation from webcam')
    parser.add_argument('--camera', type=int, default=0,
                        help='Camera device index (default: 0)')
    parser.add_argument('--resolution', type=str, default='640x480',
                        help='Camera resolution (default: 640x480)')
    parser.add_argument('--model-complexity', type=int, default=1, choices=[0, 1, 2],
                        help='MediaPipe model complexity (0=Lite, 1=Full, 2=Heavy)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Custom output directory for keypoints')
    parser.add_argument('--show-fps', action='store_true',
                        help='Display FPS counter on frame')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_arguments()

    # Set up camera with requested resolution
    cap = cv2.VideoCapture(args.camera)

    if args.resolution:
        width, height = map(int, args.resolution.split('x'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    # Initialize pose estimator with requested complexity
    estimator = PoseEstimator(model_complexity=args.model_complexity)

    # Define project-root-relative output path
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    if args.output_dir:
        ASSET_DIR = args.output_dir
    else:
        ASSET_DIR = os.path.join(PROJECT_ROOT, "..", "assets", "keypoints")
    os.makedirs(ASSET_DIR, exist_ok=True)

    session_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(ASSET_DIR, f"pose_data_{session_time}.json")
    pose_log = []

    print(f"📦 Saving session keypoints to: {output_file}")

    # FPS calculation variables
    prev_frame_time = 0
    curr_frame_time = 0

    # Main processing loop
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        # Calculate FPS
        if args.show_fps:
            curr_frame_time = time.time()
            fps = 1 / (curr_frame_time - prev_frame_time) if prev_frame_time > 0 else 0
            prev_frame_time = curr_frame_time
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        height, width, _ = frame.shape

        # Process frame for pose detection
        result = estimator.detect(frame)
        frame = estimator.draw_landmarks(frame, result, draw_style=True)

        # Extract and log keypoints
        keypoints = estimator.get_keypoints(result, width, height)
        if keypoints:
            print("🟢 Keypoints Detected:")
            keypoint_dict = {
                f"joint_{i}": {"x": x, "y": y, "z": z, "vis": vis}
                for i, (x, y, z, vis) in enumerate(keypoints)
            }
            pose_log.append(keypoint_dict)

            # Calculate joint angles if available
            angles = estimator.get_pose_angles(keypoints)
            if angles:
                # Display angles on frame
                cv2.putText(frame, f"R Elbow: {angles['right_elbow']:.1f}°", (width-200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"L Elbow: {angles['left_elbow']:.1f}°", (width-200, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Print keypoint coordinates to console
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
