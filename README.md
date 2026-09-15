# 🚗 VehicleVision: AI-Powered Real-Time Vehicle & Overload Detection System
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Backend-Flask-black.svg?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Computer_Vision-YOLOv8%20%7C%20Ultralytics-00FFFF.svg?logo=yolo" alt="YOLOv8" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg?logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/Database-SQLite%20%7C%20MySQL-orange.svg?logo=sqlite" alt="Database" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen.svg" alt="License" />
</p>
 
## 📌 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Detection & Analysis Pipeline](#-detection--analysis-pipeline)
- [Tech Stack](#-tech-stack)
- [Directory Structure](#-directory-structure)
- [Installation & Setup](#-installation--setup)
- [Configuration](#-configuration)
- [Web Interfaces & Navigation](#-web-interfaces--navigation)
- [REST API Reference](#-rest-api-reference)
- [Database Schema](#-database-schema)
- [Contributing](#-contributing)
- [License](#-license)
---
## 📖 **Project Overview**
**VehicleVision** is an end-to-end intelligent traffic surveillance and automated enforcement platform designed for smart city infrastructure, toll plazas, and highway authorities. 
Manual traffic enforcement often fails to catch fast-moving, dangerous safety violations such as **commercial cargo overloading, motorcycle triple-riding, rooftop passengers, and vehicle overcrowding**.
VehicleVision addresses this challenge by combining **state-of-the-art Deep Learning (YOLOv8)**, real-time **Multi-Object Tracking (MOT)**, and **geometric spatial association algorithms** 
to automatically identify violations, compute statutory fines, capture evidentiary snapshots, and maintain a verifiable e-challan audit trail.
---
## ✨ Key Features
- 🎯 **Multi-Class Vehicle Classification & Tracking**: Continuous identification and tracking of motorcycles, auto-rickshaws, cars, buses, trucks, and pickup vans with unique track IDs.
- 👥 **Spatial Association & Rider Counting**: Evaluates spatial relationships and IoU between detected passengers and vehicles to identify **overcrowding and triple-riding on two-wheelers**.
- 📦 **Cargo Bulge & Overload Analysis**: Inspects cargo aspect ratios, dimensional overflows, and rooftop loads compared against vehicle chassis thresholds.
- 📹 **Multi-Source Video Ingestion**:
  - **Live Browser Webcam**: Zero-driver edge client processing via HTML5 Canvas and Base64 streaming.
  - **RTSP IP Streams**: Direct ingestion from highway CCTV cameras.
  - **Video File Uploads**: Post-processing of recorded dashcam or surveillance files.
  - **Synthetic Traffic Simulator**: Built-in traffic generator for testing and demonstration.
- 🚨 **Automated Evidence & Ticket Generation**: Captures timestamped visual proof, generates unique citation IDs (`VV-XXXXXX`), and calculates statutory fines based on standard Motor Vehicles Act tariffs.
- 🛡️ **Anti-Duplicate Cooldown Engine**: Prevents redundant ticketing of the same vehicle across consecutive frames using track-ID cooldown timers.
- 📊 **Interactive Analytics Dashboard**: Live telemetry, hourly volume graphs, violation breakdowns, and peak-hour density heatmaps powered by Chart.js.
- 📑 **One-Click Report Export**: Export violation ledgers and analytical summaries into **PDF (via ReportLab), CSV, and Excel (XLSX)** formats.
- ⚙️ **Configurable Admin Rules Engine**: Modify passenger limits, fine rates, detection confidence, and alert thresholds in real time without restarting the server.
---
## 🏛️ System Architecture
┌────────────────────────────────────────────────────────────────────────┐ │ 1. VIDEO INGESTION │ │ [Browser Webcam] │ [RTSP CCTV Feeds] │ [Local Files] │ [Simulator]│ └───────────────────────────────────┬────────────────────────────────────┘ │ Frames (30 FPS) ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 2. YOLOv8 OBJECT DETECTION & TRACKING │ │ Detects bounding boxes, classes (vehicles & persons) & Track IDs │ └───────────────────────────────────┬────────────────────────────────────┘ │ Bounding boxes & Tracking Vectors ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 3. SPATIAL REASONING & OVERLOAD ANALYZER │ │ • Spatial Person-Vehicle IoU Association (Rider / Passenger Count) │ │ • Two-Wheeler Multi-Riding Check (Triple Riding > 2 riders) │ │ • Cargo Height Ratio & Horizontal Side-Bulge Detection │ │ • Vehicle-Specific Capacity & Dimension Profile Comparison │ └───────────────────────────────────┬────────────────────────────────────┘ │ Violation Triggered (if threshold exceeded) ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 4. EVIDENCE RECORDER & COOLDOWN MANAGER │ │ • Duplicate prevention cooldown (per Track ID) │ │ • Unique Citation generation (VV-XXXXXX) │ │ • High-resolution annotated snapshot capture & storage │ │ • Automatic fine calculation (based on Motor Vehicles Act rules) │ └───────────────────────────────────┬────────────────────────────────────┘ │ ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 5. FLASK BACKEND & PERSISTENCE LAYER │ │ • SQLAlchemy ORM (SQLite / MySQL) │ │ • REST APIs (Violations, Analytics, Cameras, Reporting) │ └───────────────────────────────────┬────────────────────────────────────┘ │ ▼ ┌────────────────────────────────────────────────────────────────────────┐ │ 6. USER INTERFACE & ENFORCEMENT DASHBOARD │ │ • Live Cyber HUD Stream (/video_feed) │ │ • E-Challan Workflow (/violations) │ │ • Telemetry & Peak Trend Analytics (/analytics) │ │ • On-Demand Upload Scanner (/scanner) │ │ • Export Engine (Automated PDF / Excel / CSV Reports) │ └────────────────────────────────────────────────────────────────────────┘

---
## 🔬 Detection & Analysis Pipeline
### 1. Spatial Occupancy Association
Instead of merely counting objects in isolation, VehicleVision calculates the geometric overlap (IoU) and centroid proximity between detected `person` boxes and `vehicle` boxes. If 3 or more people are associated with a motorcycle bounding box, a **Triple-Riding Safety Hazard** is flagged immediately.
### 2. Vehicle-Specific Capacity Profiles
| Vehicle Type | Standard Capacity Limit | Default Fine (INR) | Max Aspect Ratio |
|---|---|---|---|
| **Bike / Motorcycle** | 2 Persons | ₹1,000 | 1.20 |
| **Auto-Rickshaw** | 3 Persons | ₹2,000 | 1.05 |
| **Car** | 5 Persons | ₹2,000 | 0.65 |
| **Bus** | 40 Persons | ₹10,000 | 0.85 |
| **Truck / Lorry** | 2 Persons | ₹20,000 | 1.15 |
| **Pickup Van** | 3 Persons | ₹5,000 | 0.95 |
---
## 💻 Tech Stack
| Component | Technologies Used |
|---|---|
| **Backend Framework** | Python 3.9+, Flask, Flask-SQLAlchemy, Werkzeug |
| **Computer Vision & AI** | Ultralytics YOLOv8, OpenCV (`cv2`), PyTorch, TorchVision, NumPy |
| **Database** | SQLite (Default lightweight DB) / MySQL support |
| **Frontend & UI** | HTML5, Modern CSS Glassmorphism, Vanilla JavaScript, Chart.js |
| **Document Generation** | ReportLab (PDF), Pandas, OpenPyXL (Excel) |
---
## 📂 Directory Structure
```text
VehicleVision/
├── api/                    # Modular REST API Blueprints
│   ├── analytics_api.py    # Telemetry and summary endpoints
│   ├── camera_api.py       # Camera feed controls & source switching
│   ├── export_api.py       # PDF/CSV/Excel export handlers
│   └── violations_api.py   # Violation status updates and queries
├── core/                   # Core Computer Vision & Processing Logic
│   ├── detector.py         # YOLOv8 detection, tracking & HUD rendering
│   ├── evidence_recorder.py# Snapshot saver, citation builder & cooldown
│   ├── overload_analyzer.py# Spatial reasoning & overload algorithms
│   ├── sample_generator.py # Synthetic traffic generator
│   └── video_stream.py     # Background threaded stream manager
├── models/                 # Database Models (SQLAlchemy)
│   ├── camera.py           # Camera source schema
│   ├── database.py         # SQLAlchemy database instance
│   ├── traffic_log.py      # Hourly traffic volume and telemetry schema
│   └── violation.py        # Violation, fine and citation schema
├── static/                 # Static Assets & Evidence Storage
│   ├── css/                # Custom CSS styling (dark/glassmorphic themes)
│   ├── js/                 # Client scripts & charting logic
│   └── evidence/           # Auto-saved violation image snapshots & clips
├── templates/              # Jinja2 HTML UI Templates
│   ├── base.html           # Base layout and navigation shell
│   ├── index.html          # Live surveillance dashboard
│   ├── violations.html     # Violation archive and e-challan manager
│   ├── analytics.html      # Graphical metrics & charts
│   ├── scanner.html        # Manual image/video file scanner
│   └── settings.html       # Dynamic threshold & system settings
├── utils/                  # Seed data and helper scripts
├── app.py                  # Application entry point & route definitions
├── config.py               # Global settings, paths & thresholds
├── requirements.txt        # Python dependency manifest
├── yolov8n.pt              # YOLOv8 nano model weights
└── vehiclevision.db        # SQLite database file

🚀 Installation & Setup
1. Prerequisites
Python 3.9 or higher installed.
Git installed.
A functional webcam, video file, or RTSP network camera.
2. Clone the Repository
bash
git clone https://github.com/YourUsername/VehicleVision.git
cd VehicleVision
3. Create a Virtual Environment
bash
# Windows
python -m venv venv
venv\Scripts\activate
# Linux / macOS
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
bash
pip install -r requirements.txt
5. Launch the Application
bash
python app.py
Open your browser and navigate to:

http://127.0.0.1:5000
⚙️ Configuration
System parameters can be adjusted directly in config.py or updated through the /settings UI:

python
class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vehiclevision.db'
    
    # YOLO & AI Settings
    YOLO_MODEL = 'yolov8n.pt'
    CONFIDENCE_THRESHOLD = 0.40
    
    # Cooldown & Overload Thresholds
    COOLDOWN_PER_VEHICLE_SECONDS = 12.0
    OVERLOAD_SENSITIVITY = 1.0
    
    # Storage Folders
    EVIDENCE_IMG_FOLDER = 'static/evidence/images'
    EVIDENCE_VID_FOLDER = 'static/evidence/videos'

🖥️ Web Interfaces & Navigation
Route	View Name	Description
/	Live Surveillance Dashboard	Real-time MJPEG feed with HUD overlays, live alert feed, active vehicle counts, and one-click manual snapshots.
/violations	Violations Archive	Full ledger of recorded infractions with visual evidence, citation IDs, status controls (Pending/Confirmed/Dismissed), and officer notes.
/analytics	Analytics & Reports	Deep-dive telemetry, vehicle distribution charts, peak-hour heatmaps, and instant PDF/CSV/Excel report downloads.
/scanner	Offline Scanner	Drag-and-drop file upload to inspect pre-recorded video footage or single snapshot images frame by frame.
/settings	System Settings	Live reconfiguration of vehicle occupancy rules, fine tariffs, camera sources, and detection sensitivity.

🔌 REST API Reference
Video & Detection
GET /video_feed: MJPEG continuous multipart video stream with dynamic HUD overlays.
POST /api/detect-frame: Analyzes a single base64-encoded frame from client browser webcams.
GET /api/snapshot: Captures the current live frame on demand.
Violations Management
GET /api/violations: Retrieves a paginated list of violations with filtering options (status, vehicle_type, date).
GET /api/violations/<id>: Retrieves full citation and evidence details for a specific violation.
POST /api/violations/<id>/status: Updates the review status (Confirmed, Dismissed, Pending) of a violation.
Analytics & Reporting
GET /api/analytics/summary: Returns high-level metrics (total vehicles, violations, fine totals, active cameras).
GET /api/analytics/hourly: Hourly traffic density and infraction rates for charting.
GET /api/export/pdf: Generates and downloads a formal PDF enforcement summary.
GET /api/export/csv: Exports complete violation data to CSV.
GET /api/export/excel: Exports structured violation tables to an Excel .xlsx workbook.

🗄️ Database Schema

Violation Model
id (Integer, Primary Key): Auto-incrementing record ID.
citation_id (String): Unique public citation code (e.g. VV-89F1A4).
timestamp (DateTime): Exact UTC timestamp of detected violation.
vehicle_type (String): Detected class (Bike, Car, Bus, Truck, Auto).
plate_number (String): Detected or simulated vehicle license plate.
track_id (Integer): YOLO tracking vector ID.
person_count (Integer): Associated occupant/rider count.
violation_type (String): Nature of violation (e.g. Triple Riding, Overload).
estimated_overload_pct (Float): Percentage exceeded beyond capacity.
severity (String): Severity rating (Moderate, High, Critical).
fine_amount (Float): Estimated penalty in INR.
image_path (String): Relative path to evidentiary snapshot.
status (String): Workflow status (Pending, Confirmed, Dismissed).

🤝 Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch:
bash
git checkout -b feature/AmazingFeature
Commit your changes:
bash
git commit -m "Add AmazingFeature"
Push to the branch:
bash
git push origin feature/AmazingFeature
Open a Pull Request.
📄 License
This project is licensed under the MIT License - see the 

LICENSE
 file for details.
