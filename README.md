# Multi-Angle Pose Aggregation

This project implements a multi-camera human pose estimation system using Python. It simulates stereo vision using a single webcam, detects 2D pose keypoints from two different views (original and flipped), and triangulates the corresponding points to estimate accurate 3D skeletons. Everything is modular, fast, and designed to impress.

> 🔧 No stereo hardware required — second camera is simulated logically.

---

## 🚀 Features

- ✅ Real-time 2D pose detection using [MediaPipe](https://mediapipe.dev/)
- ✅ View 1: Original webcam input
- ✅ View 2: Simulated flipped version of the same frame
- ✅ Frame-by-frame triangulation into 3D joint coordinates
- ✅ JSON output for 2D and 3D poses
- ✅ Structured project layout ready for demos and extensions

---

## 📁 Project Structure

```text
multi-angle-pose-aggregation/
├── src/
│   ├── main.py               → Capture live pose + save 2D keypoints
│   ├── pose_estimation.py    → MediaPipe wrapper class
│   └── live_triangulation.py → (Optional) Live terminal output of 3D
│
├── utils/
│   ├── simulate_second_view.py   → Flip 2D keypoints to simulate second view
│   ├── triangulate_3d_pose.py    → Triangulate 3D points from both views
│   └── visualize_3d_pose.py      → Visualize 3D skeleton using Open3D
│
├── assets/
│   └── keypoints/ → Auto-saved 2D/3D JSON files
│
├── requirements.txt
└── README.md
