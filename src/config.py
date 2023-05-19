# src/config.py

"""
Configuration module for the pose estimation system.
Contains default settings and configuration loading utilities.
"""

import os
import json
from dataclasses import dataclass

@dataclass
class PoseEstimatorConfig:
    """Configuration for the PoseEstimator class."""
    static_image_mode: bool = False
    model_complexity: int = 1
    enable_segmentation: bool = False
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5

@dataclass
class CameraConfig:
    """Configuration for camera settings."""
    device_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30

@dataclass
class OutputConfig:
    """Configuration for output settings."""
    save_keypoints: bool = True
    save_images: bool = False
    output_directory: str = None
    
    def get_output_dir(self):
        """Get the output directory, creating it if necessary."""
        if self.output_directory:
            directory = self.output_directory
        else:
            # Default to project's assets/keypoints directory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            directory = os.path.join(project_root, "assets", "keypoints")
        
        os.makedirs(directory, exist_ok=True)
        return directory

@dataclass
class AppConfig:
    """Main application configuration."""
    pose: PoseEstimatorConfig = PoseEstimatorConfig()
    camera: CameraConfig = CameraConfig()
    output: OutputConfig = OutputConfig()
    show_fps: bool = False
    show_angles: bool = True
    
    @classmethod
    def from_file(cls, config_path):
        """Load configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            pose_config = PoseEstimatorConfig(**config_data.get('pose', {}))
            camera_config = CameraConfig(**config_data.get('camera', {}))
            output_config = OutputConfig(**config_data.get('output', {}))
            
            return cls(
                pose=pose_config,
                camera=camera_config,
                output=output_config,
                show_fps=config_data.get('show_fps', False),
                show_angles=config_data.get('show_angles', True)
            )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}")
            return cls()  # Return default config
    
    def save_to_file(self, config_path):
        """Save configuration to a JSON file."""
        config_data = {
            'pose': {
                'static_image_mode': self.pose.static_image_mode,
                'model_complexity': self.pose.model_complexity,
                'enable_segmentation': self.pose.enable_segmentation,
                'min_detection_confidence': self.pose.min_detection_confidence,
                'min_tracking_confidence': self.pose.min_tracking_confidence
            },
            'camera': {
                'device_id': self.camera.device_id,
                'width': self.camera.width,
                'height': self.camera.height,
                'fps': self.camera.fps
            },
            'output': {
                'save_keypoints': self.output.save_keypoints,
                'save_images': self.output.save_images,
                'output_directory': self.output.output_directory
            },
            'show_fps': self.show_fps,
            'show_angles': self.show_angles
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
# Enhanced configuration
# Enhanced configuration
