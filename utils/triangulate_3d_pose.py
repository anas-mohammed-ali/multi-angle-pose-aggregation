# utils/triangulate_3d_pose.py

import json
import numpy as np
import os

def load_keypoints(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def triangulate_point(p1, p2, cam_matrix1, cam_matrix2):
    # Build the linear system Ap = 0
    A = np.array([
        (p1[0] * cam_matrix1[2] - cam_matrix1[0]),
        (p1[1] * cam_matrix1[2] - cam_matrix1[1]),
        (p2[0] * cam_matrix2[2] - cam_matrix2[0]),
        (p2[1] * cam_matrix2[2] - cam_matrix2[1])
    ])
    _, _, Vt = np.linalg.svd(A)
    X = Vt[-1]
    X = X / X[3]
    return X[:3]  # x, y, z

def triangulate_all_frames(view1_data, view2_data, cam_matrix1, cam_matrix2):
    triangulated_poses = []

    for frame1, frame2 in zip(view1_data, view2_data):
        joints_3d = {}
        for joint_name in frame1.keys():
            if joint_name not in frame2:
                continue

            x1, y1 = frame1[joint_name]['x'], frame1[joint_name]['y']
            x2, y2 = frame2[joint_name]['x'], frame2[joint_name]['y']

            p1 = np.array([x1, y1])
            p2 = np.array([x2, y2])

            point_3d = triangulate_point(p1, p2, cam_matrix1, cam_matrix2)
            joints_3d[joint_name] = {
                'X': float(point_3d[0]),
                'Y': float(point_3d[1]),
                'Z': float(point_3d[2])
            }

        triangulated_poses.append(joints_3d)

    return triangulated_poses

def save_to_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Triangulated 3D pose saved to: {path}")

if __name__ == "__main__":
    # ---- CONFIG ----
    original_filename = "pose_data_20250425-084538.json"  # change to match your real filename
    flipped_filename  = "pose_data_20250425-084538_flipped.json"

    # Use approx width to generate camera matrices
    frame_width = 640
    focal_length = frame_width  # fake focal length (same as width)
    cx, cy = frame_width // 2, 360  # approximate image center

    # Camera matrices (simplified pinhole intrinsics)
    cam_matrix1 = np.array([[focal_length, 0, cx, 0],
                            [0, focal_length, cy, 0],
                            [0, 0, 1, 0]])

    baseline = 5.0  # cm between simulated cameras

    cam_matrix2 = np.array([[focal_length, 0, cx, -focal_length * baseline],
                            [0, focal_length, cy, 0],
                            [0, 0, 1, 0]])

    # ---- Load Keypoints ----
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    kp_dir = os.path.join(PROJECT_ROOT, "..", "assets", "keypoints")

    view1_data = load_keypoints(os.path.join(kp_dir, original_filename))
    view2_data = load_keypoints(os.path.join(kp_dir, flipped_filename))

    # ---- Triangulate ----
    triangulated_3d = triangulate_all_frames(view1_data, view2_data, cam_matrix1, cam_matrix2)

    # ---- Save ----
    output_file = os.path.join(kp_dir, original_filename.replace(".json", "_3d.json"))
    save_to_json(triangulated_3d, output_file)
