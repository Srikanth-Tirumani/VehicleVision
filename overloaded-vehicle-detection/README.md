# Overload Guardian AI - Intelligent Overloaded Vehicle Detection & Enforcement

An advanced AI-powered computer vision and deep learning platform designed to detect overloaded vehicles in real-time. The system automatically inspects passenger occupancy and cargo thresholds, records forensic photo & video evidence, logs incident metadata, and displays real-time telemetry on an ultra-modern web dashboard.

---

## ✨ Features & Upgrades

- 🧠 **YOLOv8 Object Detection**: Real-time identification of multi-class vehicles (Bikes, Autos, Cars, Vans, Buses, Trucks) and passenger/cargo entities.
- 🚨 **Intelligent Overload Heuristics**:
  - **Bikes / Two-Wheelers**: Real-time detection of illegal triple-riding (>2 persons).
  - **Auto-Rickshaws & Cars**: Passenger and luggage capacity overload enforcement.
  - **Commercial Trucks & Buses**: Severe cargo overload and roof/passenger violations.
- 📹 **Live Web Stream**: High-performance browser MJPEG stream (`/video_feed`) featuring interactive HUD overlays, bounding boxes, passenger counts, and violation alerts.
- ⚡ **Non-Blocking Evidence Capture**: Rolling in-memory frame buffer recording photo snapshots and MP4 video clips asynchronously without stuttering video feeds.
- 📊 **Modern Glassmorphism Dashboard**:
  - Live KPI summary counters (Total incidents, Today's violations, Top infraction categories).
  - Dynamic **Chart.js** vehicle distribution visualization.
  - Interactive Evidence Table with full-text search, vehicle type filters, and date pickers.
  - **Evidence Media Modals**: High-resolution image viewer and built-in HTML5 video player.
  - **1-Click CSV Export**: Download structured incident logs.
  - **Dynamic Feed Switcher**: Switch between Webcams, MP4 video files, or RTSP camera feeds live from the browser UI.
- 🗄️ **Dual Database Architecture**: Works out-of-the-box with zero-config local **SQLite** with automatic fallback, and supports production **MySQL** databases.

---

## 🛠️ Technology Stack

- **Computer Vision & AI**: Python, OpenCV, YOLOv8 (Ultralytics)
- **Web Backend & Streaming**: Flask, Multi-threaded MJPEG Streamer, REST API
- **Database Layer**: SQLite3 & MySQL Connector
- **Frontend UI**: Modern Glassmorphism CSS, JavaScript (ES6+), FontAwesome 6, Chart.js

---

## 📂 Project Structure

```text
Overload_vehicle_detection/
├── app.py                      # Desktop OpenCV GUI mode launcher
├── run.py                      # Unified one-click Web & AI system runner
├── traffic_demo.mp4            # Sample traffic video footage
│
└── overloaded-vehicle-detection/
    ├── app.py                  # Core standalone OpenCV application
    ├── config.py               # Central settings (Camera source, DB config, Server port)
    ├── run.py                  # Web application & AI worker runner
    ├── requirements.txt        # Python package dependencies
    ├── yolov8n.pt              # YOLOv8 neural network weights
    │
    ├── my_utils/
    │   ├── detector.py         # AI detection pipeline & async evidence recorder
    │   ├── tracker.py          # Object tracker with violation debouncing
    │   ├── rules.py            # Vehicle capacity thresholds & violation reasons
    │   └── database.py         # DB connection manager, schema migration & CRUD APIs
    │
    └── webapp/
        ├── server.py           # Flask web server, video streaming route & REST endpoints
        ├── captures/           # Saved forensic evidence (photos and videos)
        │   ├── photos/
        │   └── videos/
        └── templates/
            └── dashboard.html  # Glassmorphism dark web control center
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r overloaded-vehicle-detection/requirements.txt
```

### 2. Launch the System (Web Dashboard + AI Live Stream)
Run from project root:
```bash
python run.py
```
Or inside the subfolder:
```bash
python overloaded-vehicle-detection/run.py
```
👉 Open your browser at **http://localhost:5000** to view the live dashboard and camera stream.

---

### 3. Run Standalone Desktop OpenCV Window
If you prefer a native desktop window for testing:
```bash
python app.py --source traffic_demo.mp4
# Or use integrated webcam:
python app.py --source 0
```
- Press **`q`** or **`ESC`** in the video window to stop.

---

## ⚙️ Configuration (`config.py`)

```python
# Database connection settings (Falls back to SQLite automatically if MySQL is unavailable)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "overload_db"
}

# Default input source (0 for Webcam, "traffic_demo.mp4", or "rtsp://...")
CAMERA_SOURCE = "traffic_demo.mp4"

# Video evidence recording duration
CAPTURE_FPS = 20
CAPTURE_SECONDS = 4
```

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web Control Center & Live Dashboard |
| `GET` | `/video_feed` | Multipart MJPEG real-time AI video stream |
| `GET` | `/api/records` | Get all violation incident records |
| `GET` | `/api/stats` | Get KPI metrics and vehicle breakdown stats |
| `DELETE`| `/api/records/<id>` | Delete incident entry and clean up stored media |
| `POST` | `/api/source` | Switch camera/video source dynamically |
| `GET` | `/api/export/csv` | Download CSV violation report |

---

## 🛡️ License & Credits
Developed for intelligent road safety monitoring and traffic enforcement.
