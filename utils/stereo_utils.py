# utils/stereo_utils.py

"""
Utilities for stereo vision processing.
"""

import cv2
import numpy as np
import json
import os

def create_stereo_camera_matrices(baseline, focal_length, cx, cy):
    """
    Create camera matrices for a stereo setup.
    
    Args:
        baseline: Distance between cameras in cm
        focal_length: Focal length in pixels
        cx, cy: Principal point coordinates
        
    Returns:
        Tuple of (left_camera_matrix, right_camera_matrix)
    """
    # Left camera matrix (identity rotation, zero translation)
    left_camera_matrix = np.array([
        [focal_length, 0, cx, 0],
        [0, focal_length, cy, 0],
        [0, 0, 1, 0]
    ])
    
    # Right camera matrix (identity rotation, translation along X-axis)
    right_camera_matrix = np.array([
        [focal_length, 0, cx, -focal_length * baseline],
        [0, focal_length, cy, 0],
        [0, 0, 1, 0]
    ])
    
    return left_camera_matrix, right_camera_matrix

def triangulate_points(points_left, points_right, camera_matrix_left, camera_matrix_right):
    """
    Triangulate 3D points from corresponding points in stereo images.
    
    Args:
        points_left: Array of points from left image (Nx2)
        points_right: Array of points from right image (Nx2)
        camera_matrix_left: Left camera matrix (3x4)
        camera_matrix_right: Right camera matrix (3x4)
        
    Returns:
        Array of 3D points (Nx3)
    """
    # Triangulate each point
    points_3d = []
    for pt_left, pt_right in zip(points_left, points_right):
        # Build the linear system Ax = 0
        A = np.array([
            pt_left[0] * camera_matrix_left[2] - camera_matrix_left[0],
            pt_left[1] * camera_matrix_left[2] - camera_matrix_left[1],
            pt_right[0] * camera_matrix_right[2] - camera_matrix_right[0],
            pt_right[1] * camera_matrix_right[2] - camera_matrix_right[1]
        ])
        
        # Solve using SVD
        _, _, Vt = np.linalg.svd(A)
        X = Vt[-1]
        X = X / X[3]  # Normalize homogeneous coordinates
        
        points_3d.append(X[:3])
    
    return np.array(points_3d)

def compute_disparity_map(left_image, right_image, min_disparity=0, num_disparities=64, block_size=5):
    """
    Compute disparity map from stereo images.
    
    Args:
        left_image: Left stereo image
        right_image: Right stereo image
        min_disparity: Minimum disparity value
        num_disparities: Number of disparity values
        block_size: Block size for matching
        
    Returns:
        Disparity map
    """
    # Convert to grayscale if needed
    if len(left_image.shape) == 3:
        left_gray = cv2.cvtColor(left_image, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_image, cv2.COLOR_BGR2GRAY)
    else:
        left_gray = left_image
        right_gray = right_image
    
    # Create StereoBM object
    stereo = cv2.StereoBM_create(
        numDisparities=num_disparities,
        blockSize=block_size
    )
    stereo.setMinDisparity(min_disparity)
    
    # Compute disparity map
    disparity = stereo.compute(left_gray, right_gray)
    
    # Normalize for display
    disparity_normalized = cv2.normalize(
        disparity, 
        None, 
        alpha=0, 
        beta=255, 
        norm_type=cv2.NORM_MINMAX, 
        dtype=cv2.CV_8U
    )
    
    return disparity, disparity_normalized

def depth_from_disparity(disparity, baseline, focal_length):
    """
    Convert disparity map to depth map.
    
    Args:
        disparity: Disparity map
        baseline: Distance between cameras in cm
        focal_length: Focal length in pixels
        
    Returns:
        Depth map in cm
    """
    # Avoid division by zero
    disparity_masked = disparity.copy()
    disparity_masked[disparity_masked == 0] = 0.1
    
    # Calculate depth: depth = baseline * focal_length / disparity
    depth = baseline * focal_length / disparity_masked
    
    return depth

def save_point_cloud(points_3d, colors, filename):
    """
    Save 3D points as a PLY file.
    
    Args:
        points_3d: Array of 3D points (Nx3)
        colors: Array of RGB colors (Nx3)
        filename: Output PLY file path
    """
    with open(filename, 'w') as f:
        # Write header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(points_3d)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property uchar red\n")
        f.write("property uchar green\n")
        f.write("property uchar blue\n")
        f.write("end_header\n")
        
        # Write points
        for point, color in zip(points_3d, colors):
            f.write(f"{point[0]} {point[1]} {point[2]} {color[0]} {color[1]} {color[2]}\n")

def simulate_second_view(keypoints, frame_width, flip_horizontally=True):
    """
    Simulate a second view by flipping keypoints horizontally.
    
    Args:
        keypoints: Dictionary of keypoints
        frame_width: Width of the frame
        flip_horizontally: Whether to flip horizontally (True) or vertically (False)
        
    Returns:
        Dictionary of flipped keypoints
    """
    flipped = {}
    
    if flip_horizontally:
        # Horizontal flip (simulates side-by-side cameras)
        for joint, coords in keypoints.items():
            flipped[joint] = {
                "x": frame_width - coords["x"],
                "y": coords["y"],
                "z": coords["z"],
                "vis": coords["vis"]
            }
    else:
        # Vertical flip (simulates top-bottom cameras)
        frame_height = 480  # Default height, can be parameterized
        for joint, coords in keypoints.items():
            flipped[joint] = {
                "x": coords["x"],
                "y": frame_height - coords["y"],
                "z": coords["z"],
                "vis": coords["vis"]
            }
    
    return flipped

if __name__ == "__main__":
    # Example usage
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Load keypoints from a file
    keypoints_file = os.path.join(PROJECT_ROOT, "assets", "keypoints", "pose_data_example.json")
    
    try:
        with open(keypoints_file, 'r') as f:
            keypoints_data = json.load(f)
            
        # Process first frame
        if keypoints_data:
            frame_width = 640  # Default width
            flipped_keypoints = simulate_second_view(keypoints_data[0], frame_width)
            print("Original keypoints:", keypoints_data[0])
            print("Flipped keypoints:", flipped_keypoints)
    except FileNotFoundError:
        print(f"File not found: {keypoints_file}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {keypoints_file}")
