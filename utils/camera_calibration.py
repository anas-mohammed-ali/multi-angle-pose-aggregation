# utils/camera_calibration.py

"""
Camera calibration utilities for stereo vision setup.
"""

import cv2
import numpy as np
import os
import glob
import json

class CameraCalibrator:
    """
    Class for calibrating cameras using chessboard patterns.
    """
    def __init__(self, chessboard_size=(9, 6), square_size=2.5):
        """
        Initialize the calibrator.
        
        Args:
            chessboard_size: Tuple (width, height) of chessboard corners
            square_size: Size of chessboard squares in cm
        """
        self.chessboard_size = chessboard_size
        self.square_size = square_size
        
        # Prepare object points (0,0,0), (1,0,0), (2,0,0) ...
        self.objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
        self.objp *= square_size  # Scale to real-world units
        
        # Arrays to store object points and image points
        self.objpoints = []  # 3D points in real world space
        self.imgpoints = []  # 2D points in image plane
        
        # Calibration results
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rvecs = None
        self.tvecs = None
        
    def add_calibration_image(self, image):
        """
        Process a calibration image and extract chessboard corners.
        
        Args:
            image: Input image containing chessboard
            
        Returns:
            bool: True if corners were found, False otherwise
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners(
            gray, 
            self.chessboard_size, 
            None
        )
        
        if ret:
            # Refine corner positions
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            # Add to calibration data
            self.objpoints.append(self.objp)
            self.imgpoints.append(corners)
            
            # Draw corners on image for visualization
            cv2.drawChessboardCorners(image, self.chessboard_size, corners, ret)
            
        return ret, image
    
    def calibrate(self, image_shape):
        """
        Perform camera calibration using collected points.
        
        Args:
            image_shape: Tuple (height, width) of the images
            
        Returns:
            bool: True if calibration was successful
        """
        if len(self.objpoints) < 5:
            print("Need at least 5 calibration images")
            return False
            
        ret, self.camera_matrix, self.dist_coeffs, self.rvecs, self.tvecs = cv2.calibrateCamera(
            self.objpoints, 
            self.imgpoints, 
            image_shape[::-1],  # Width, height
            None, 
            None
        )
        
        return ret
    
    def save_calibration(self, filename):
        """
        Save calibration results to a JSON file.
        
        Args:
            filename: Output JSON file path
        """
        if self.camera_matrix is None:
            print("No calibration data to save")
            return False
            
        calibration_data = {
            "camera_matrix": self.camera_matrix.tolist(),
            "dist_coeffs": self.dist_coeffs.tolist(),
            "image_shape": self.imgpoints[0].shape[0:2]
        }
        
        with open(filename, 'w') as f:
            json.dump(calibration_data, f, indent=2)
            
        return True
    
    def load_calibration(self, filename):
        """
        Load calibration results from a JSON file.
        
        Args:
            filename: Input JSON file path
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            self.camera_matrix = np.array(data["camera_matrix"])
            self.dist_coeffs = np.array(data["dist_coeffs"])
            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False
            
    def undistort_image(self, image):
        """
        Undistort an image using the calibration data.
        
        Args:
            image: Input image to undistort
            
        Returns:
            Undistorted image
        """
        if self.camera_matrix is None:
            print("No calibration data available")
            return image
            
        return cv2.undistort(
            image, 
            self.camera_matrix, 
            self.dist_coeffs, 
            None, 
            self.camera_matrix
        )

def calibrate_from_images(image_dir, output_file, chessboard_size=(9, 6), square_size=2.5):
    """
    Calibrate a camera from a directory of chessboard images.
    
    Args:
        image_dir: Directory containing calibration images
        output_file: Path to save calibration results
        chessboard_size: Tuple (width, height) of chessboard corners
        square_size: Size of chessboard squares in cm
        
    Returns:
        bool: True if calibration was successful
    """
    calibrator = CameraCalibrator(chessboard_size, square_size)
    
    # Find all images in directory
    image_paths = glob.glob(os.path.join(image_dir, '*.jpg')) + \
                 glob.glob(os.path.join(image_dir, '*.png'))
    
    if not image_paths:
        print(f"No images found in {image_dir}")
        return False
        
    print(f"Found {len(image_paths)} images for calibration")
    
    # Process each image
    successful_images = 0
    for img_path in image_paths:
        image = cv2.imread(img_path)
        if image is None:
            print(f"Could not read {img_path}")
            continue
            
        ret, _ = calibrator.add_calibration_image(image)
        if ret:
            successful_images += 1
            print(f"Processed {img_path} - {successful_images}/{len(image_paths)}")
        else:
            print(f"Could not find chessboard in {img_path}")
    
    if successful_images < 5:
        print("Not enough successful calibration images")
        return False
        
    # Calibrate camera
    image_shape = cv2.imread(image_paths[0]).shape[:2]
    ret = calibrator.calibrate(image_shape)
    
    if ret:
        # Save calibration
        calibrator.save_calibration(output_file)
        print(f"Calibration saved to {output_file}")
        return True
    else:
        print("Calibration failed")
        return False

if __name__ == "__main__":
    # Example usage
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    calibrate_from_images(
        os.path.join(PROJECT_ROOT, "assets", "calibration"),
        os.path.join(PROJECT_ROOT, "assets", "camera_calibration.json")
    )
