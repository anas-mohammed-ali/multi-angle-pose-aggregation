# utils/visualize_3d_pose.py

import json
import os
import open3d as o3d
import numpy as np

def load_3d_keypoints(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_skeleton_lines():
    # MediaPipe Pose connection indices (0–32) simplified
    # Source: https://google.github.io/mediapipe/solutions/pose.html
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 7),     # right arm
        (0, 4), (4, 5), (5, 6), (6, 8),     # left arm
        (9, 10), (11, 12),                 # shoulders
        (11, 13), (13, 15), (15, 17),      # right leg
        (12, 14), (14, 16), (16, 18),      # left leg
        (23, 24), (24, 26), (26, 28),      # right lower leg
        (23, 25), (25, 27), (27, 29),      # left lower leg
    ]
    return connections

def visualize_pose_3d(keypoints_3d, frame_id=0):
    frame = keypoints_3d[frame_id]  # visualize first frame by default

    joint_positions = []
    for i in range(33):  # Total joints
        joint_name = f"joint_{i}"
        if joint_name in frame:
            p = frame[joint_name]
            joint_positions.append([p['X'], p['Y'], p['Z']])
        else:
            joint_positions.append([0, 0, 0])  # Placeholder

    joint_positions = np.array(joint_positions)

    # Create point cloud
    points = o3d.geometry.PointCloud()
    points.points = o3d.utility.Vector3dVector(joint_positions)
    points.paint_uniform_color([0.1, 0.7, 0.9])  # Light blue

    # Create lines
    lines = create_skeleton_lines()
    line_set = o3d.geometry.LineSet(
        points=o3d.utility.Vector3dVector(joint_positions),
        lines=o3d.utility.Vector2iVector(lines),
    )
    line_set.paint_uniform_color([1.0, 0.6, 0.0])  # Orange

    # Visualize
    o3d.visualization.draw_geometries([points, line_set])

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    input_file = "pose_data_20250425-084538_3d.json"  # update to your actual file
    path = os.path.join(PROJECT_ROOT, "..", "assets", "keypoints", input_file)

    keypoints_3d = load_3d_keypoints(path)
    visualize_pose_3d(keypoints_3d)
