# webapp/server.py
import sys
import os
import time
import io
import csv
import threading
import cv2
from flask import Flask, render_template, Response, jsonify, request, send_from_directory, make_response

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import CAMERA_SOURCE, SERVER_HOST, SERVER_PORT
from my_utils.database import init_db, get_all_records, get_statistics, delete_record_by_id
from my_utils.detector import process_frame

app = Flask(__name__, template_folder="templates", static_folder="static")

CAPTURES_DIR = os.path.join(BASE_DIR, "webapp", "captures")
os.makedirs(os.path.join(CAPTURES_DIR, "photos"), exist_ok=True)
os.makedirs(os.path.join(CAPTURES_DIR, "videos"), exist_ok=True)

# Global Stream State Manager
class StreamManager:
    def __init__(self, initial_source=CAMERA_SOURCE):
        self.source = initial_source
        self.cap = None
        self.lock = threading.Lock()
        self.running = True
        self.current_frame = None
        self.frame_idx = 0
        self.is_active = False
        self.init_capture()

    def init_capture(self):
        with self.lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass

            src = self.source
            if isinstance(src, str) and src.isdigit():
                src = int(src)

            if isinstance(src, int):
                # Try DirectShow on Windows for webcam
                self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(src)
            else:
                # Video file or URL
                video_path = src
                if not os.path.isabs(video_path):
                    video_path = os.path.join(BASE_DIR, video_path)
                self.cap = cv2.VideoCapture(video_path if os.path.exists(video_path) else src)

            self.frame_idx = 0
            self.is_active = self.cap.isOpened() if self.cap else False

    def change_source(self, new_source):
        self.source = new_source
        self.init_capture()
        return self.is_active

    def get_frame(self):
        with self.lock:
            if not self.cap or not self.cap.isOpened():
                self.init_capture()
                if not self.cap or not self.cap.isOpened():
                    return None

            ret, frame = self.cap.read()
            if not ret:
                # If it's a video file, loop it automatically
                if isinstance(self.source, str) and not self.source.isdigit():
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                    if not ret:
                        return None
                else:
                    return None

            self.frame_idx += 1
            annotated = process_frame(frame, self.frame_idx, self.cap)
            self.current_frame = annotated
            return annotated

stream_manager = StreamManager()

# Background thread to keep stream processing active even when no browser is viewing
def background_stream_worker():
    while True:
        try:
            stream_manager.get_frame()
            time.sleep(0.035)  # ~28 FPS processing rate
        except Exception as e:
            time.sleep(0.1)

worker_thread = threading.Thread(target=background_stream_worker, daemon=True)
worker_thread.start()

def generate_mjpeg_stream():
    """Generator for streaming live multipart JPEG frames to browser."""
    while True:
        frame = stream_manager.current_frame
        if frame is None:
            # Generate placeholder frame if stream is offline
            placeholder = 30 * cv2.imread(os.path.join(BASE_DIR, "webapp", "static", "placeholder.jpg")) if os.path.exists(os.path.join(BASE_DIR, "webapp", "static", "placeholder.jpg")) else None
            if placeholder is None:
                import numpy as np
                placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(placeholder, "AI Camera Feed Connecting / Idle...", (80, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            frame = placeholder

        # Compress to JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        if not ret:
            time.sleep(0.05)
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/video_feed")
def video_feed():
    """Live MJPEG video stream route for browser."""
    return Response(generate_mjpeg_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/captures/<path:filename>")
def serve_capture(filename):
    """Safely serves captured violation photos and videos."""
    return send_from_directory(CAPTURES_DIR, filename)

# REST API Endpoints
@app.route("/api/records", methods=["GET"])
def api_records():
    records = get_all_records(limit=300)
    return jsonify({"success": True, "records": records, "count": len(records)})

@app.route("/api/stats", methods=["GET"])
def api_stats():
    stats = get_statistics()
    stats["stream_active"] = stream_manager.is_active
    stats["current_source"] = str(stream_manager.source)
    return jsonify({"success": True, "stats": stats})

@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def api_delete_record(record_id):
    deleted = delete_record_by_id(record_id)
    if deleted:
        # Optionally remove physical files
        for key in ("photo_path", "video_path"):
            val = deleted.get(key)
            if val:
                rel = val.replace("captures/", "")
                file_to_remove = os.path.join(CAPTURES_DIR, rel)
                if os.path.exists(file_to_remove):
                    try:
                        os.remove(file_to_remove)
                    except Exception:
                        pass
        return jsonify({"success": True, "message": f"Record #{record_id} deleted successfully."})
    return jsonify({"success": False, "message": "Record not found"}), 404

@app.route("/api/source", methods=["POST"])
def api_change_source():
    data = request.get_json() or {}
    new_src = data.get("source", "").strip()
    if not new_src:
        return jsonify({"success": False, "message": "Source cannot be empty."}), 400

    success = stream_manager.change_source(new_src)
    return jsonify({
        "success": success,
        "source": new_src,
        "message": f"Switched source to: {new_src}" if success else f"Failed opening source: {new_src}"
    })

@app.route("/api/export/csv", methods=["GET"])
def api_export_csv():
    records = get_all_records(limit=2000)
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Vehicle Type", "Passengers", "Cargo Weight (kg)", "Violation Reason", "Confidence", "Timestamp", "Photo Evidence", "Video Evidence"])

    for r in records:
        writer.writerow([
            r.get("id", ""),
            r.get("vehicle_type", ""),
            r.get("passengers", 0),
            r.get("cargo_weight", 0),
            r.get("violation_reason", ""),
            f"{r.get('confidence', 0):.2f}",
            r.get("timestamp", ""),
            r.get("photo_path", ""),
            r.get("video_path", "")
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=overload_violations_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == "__main__":
    init_db()
    print(f"🚀 Starting Overload Detection Web Server on http://localhost:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, threaded=True)
