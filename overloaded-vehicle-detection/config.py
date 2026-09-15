# config.py
import os

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "dineshkm@77",
    "database": "overload_db"
}

# Camera source:
# - 0 or 1 for integrated/USB Webcam
# - "traffic_demo.mp4" or "sample_traffic.mp4" for local video testing
# - "rtsp://admin:pass@192.168.1.100:554/live" for CCTV / IP Camera feed
CAMERA_SOURCE = "traffic_demo.mp4"

# Video evidence settings for recorded clips
CAPTURE_FPS = 20
CAPTURE_SECONDS = 4  # Seconds of video to capture surrounding violation

# Web Server Settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
