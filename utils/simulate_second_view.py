# utils/simulate_second_view.py

import json
import os

def flip_keypoints_horizontally(keypoints, frame_width):
    flipped = {}
    for joint, coords in keypoints.items():
        x_flipped = frame_width - coords["x"]
        flipped[joint] = {
            "x": x_flipped,
            "y": coords["y"],
            "z": coords["z"],
            "vis": coords["vis"]
        }
    return flipped

def simulate_second_view(json_path, frame_width):
    with open(json_path, 'r') as f:
        original_data = json.load(f)

    flipped_data = []

    for frame in original_data:
        flipped_frame = flip_keypoints_horizontally(frame, frame_width)
        flipped_data.append(flipped_frame)

    # Save to a new file in the same directory
    flipped_path = json_path.replace(".json", "_flipped.json")
    with open(flipped_path, 'w') as f:
        json.dump(flipped_data, f, indent=2)

    print(f"✅ Simulated flipped keypoints saved to: {flipped_path}")
    return flipped_path

if __name__ == "__main__":
    # 👇 Use real filename from your saved data
    original_filename = "pose_data_20250425-084538.json"  # ← change to match your real file

    # 📍 Dynamically build absolute file path
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(PROJECT_ROOT, "..", "assets", "keypoints", original_filename)

    frame_width = 640  # ← change this if your webcam width is different

    simulate_second_view(input_path, frame_width)
