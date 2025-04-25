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
```

---

## ⚙️ Installation

Make sure you have Python 3.8+ installed. Then:

```bash
git clone https://github.com/anas-mohammed-ali/multi-angle-pose-aggregation.git
cd multi-angle-pose-aggregation
pip install -r requirements.txt
```

---

## ▶️ How to Use

### 🟢 1. Capture 2D Keypoints from Webcam

```bash
python src/main.py
```

- Press `Q` to stop recording  
- JSON will be saved inside:  
  `assets/keypoints/pose_data_<timestamp>.json`

---

### 🔁 2. Simulate Second View

```bash
python utils/simulate_second_view.py
```

- Edit the script to insert your actual filename and frame width

---

### 📐 3. Triangulate 3D Poses

```bash
python utils/triangulate_3d_pose.py
```

- Set your original and flipped filenames in the script

---

### 🧱 4. Visualize 3D Skeleton

```bash
python utils/visualize_3d_pose.py
```

- Visualizes the first frame (or you can modify to loop through all)

---

## 📸 Demo

*Coming soon: GIF of 2D overlay + 3D Open3D visualizer side-by-side.*

---

## 📄 License

This project is under the MIT License — use it, modify it, build on it!

---

## 💼 Author

**Anas Mohammed Ali**  
M.Sc. Embedded Systems — Saarland University  
[LinkedIn](https://www.linkedin.com/in/anas-mohammed-ali) · [GitHub](https://github.com/anas-mohammed-ali)
