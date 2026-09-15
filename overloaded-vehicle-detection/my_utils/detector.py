# my_utils/detector.py
import os
import time
import threading
from collections import deque
import cv2
import numpy as np
from ultralytics import YOLO

from my_utils.tracker import SimpleTracker
from my_utils.rules import check_overload
from my_utils.database import insert_overloaded
from config import CAPTURE_FPS, CAPTURE_SECONDS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO_DIR = os.path.join(BASE_DIR, "webapp", "captures", "photos")
VIDEO_DIR = os.path.join(BASE_DIR, "webapp", "captures", "videos")
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Load lightweight YOLOv8 model
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
model = YOLO(MODEL_PATH if os.path.exists(MODEL_PATH) else "yolov8n.pt")

tracker = SimpleTracker(iou_thresh=0.25, max_misses=10)

# Rolling frame buffer for asynchronous video evidence generation (pre-event buffer)
FRAME_BUFFER_MAX = CAPTURE_FPS * (CAPTURE_SECONDS + 2)
frame_buffer = deque(maxlen=FRAME_BUFFER_MAX)
buffer_lock = threading.Lock()

def map_label(label):
    """Maps COCO classes to our vehicle types."""
    l = label.lower()
    if l in ("motorbike", "motorcycle", "bicycle"):
        return "bike"
    if l == "bus":
        return "bus"
    if l in ("truck", "trailer"):
        return "truck"
    if l in ("van", "minivan"):
        return "van"
    if l in ("car", "taxi"):
        return "car"
    return None

def expand_bbox(bbox, pad, w, h):
    x1, y1, x2, y2 = bbox
    return [
        max(0, x1 - pad),
        max(0, y1 - pad),
        min(w - 1, x2 + pad),
        min(h - 1, y2 + pad)
    ]

def save_photo_evidence(frame, prefix):
    """Saves high-res snapshot and returns relative path for web serving."""
    ts = int(time.time() * 1000)
    filename = f"{prefix}_{ts}.jpg"
    full_path = os.path.join(PHOTO_DIR, filename)
    cv2.imwrite(full_path, frame)
    return f"captures/photos/{filename}"

def async_write_video_clip(frames_to_write, output_path, fps=20):
    """Worker thread function to write frames to video file without blocking main pipeline."""
    try:
        if not frames_to_write:
            return
        h, w = frames_to_write[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        for f in frames_to_write:
            out.write(f)
        out.release()
    except Exception as e:
        print(f"Error writing async video clip: {e}")

def save_video_evidence_async(prefix, duration_sec=CAPTURE_SECONDS, fps=CAPTURE_FPS):
    """Extracts recent frames from rolling buffer and writes video clip asynchronously."""
    ts = int(time.time() * 1000)
    filename = f"{prefix}_{ts}.mp4"
    full_path = os.path.join(VIDEO_DIR, filename)

    with buffer_lock:
        frames_snapshot = list(frame_buffer)

    target_count = min(len(frames_snapshot), int(duration_sec * fps))
    if target_count > 0:
        frames_slice = frames_snapshot[-target_count:]
        t = threading.Thread(target=async_write_video_clip, args=(frames_slice, full_path, fps), daemon=True)
        t.start()
        return f"captures/videos/{filename}"
    return ""

def draw_hud_box(image, bbox, label_text, is_overloaded=False, sub_text=None):
    """Renders modern, semi-transparent HUD bounding box with badges."""
    x1, y1, x2, y2 = bbox
    color = (40, 40, 235) if is_overloaded else (40, 200, 70)  # Red / Green in BGR
    accent_color = (0, 0, 255) if is_overloaded else (0, 230, 100)

    # Main vehicle box
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)

    # Top corner accents
    corner_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
    cv2.line(image, (x1, y1), (x1 + corner_len, y1), accent_color, 4)
    cv2.line(image, (x1, y1), (x1, y1 + corner_len), accent_color, 4)
    cv2.line(image, (x2, y1), (x2 - corner_len, y1), accent_color, 4)
    cv2.line(image, (x2, y1), (x2, y1 + corner_len), accent_color, 4)
    cv2.line(image, (x1, y2), (x1 + corner_len, y2), accent_color, 4)
    cv2.line(image, (x1, y2), (x1, y2 - corner_len), accent_color, 4)
    cv2.line(image, (x2, y2), (x2 - corner_len, y2), accent_color, 4)
    cv2.line(image, (x2, y2), (x2, y2 - corner_len), accent_color, 4)

    # Label badge background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.52
    thickness = 1
    (tw, th), _ = cv2.getTextSize(label_text, font, font_scale, thickness)

    badge_h = th + 10
    badge_w = tw + 14
    bx1 = x1
    by1 = max(0, y1 - badge_h)
    bx2 = min(image.shape[1] - 1, bx1 + badge_w)
    by2 = max(badge_h, y1)

    # Badge overlay
    sub_img = image[by1:by2, bx1:bx2]
    badge_bg = np.zeros_like(sub_img)
    badge_bg[:] = (20, 20, 20) if not is_overloaded else (30, 20, 160)
    cv2.addWeighted(sub_img, 0.25, badge_bg, 0.75, 0, sub_img)

    text_color = (255, 255, 255)
    cv2.putText(image, label_text, (bx1 + 6, by2 - 5), font, font_scale, text_color, thickness, cv2.LINE_AA)

    # Sub-text badge (if overloaded status or stats)
    if sub_text:
        (sw, sh), _ = cv2.getTextSize(sub_text, font, 0.45, 1)
        sx1 = x1
        sy1 = min(image.shape[0] - 1, y2)
        sx2 = min(image.shape[1] - 1, sx1 + sw + 10)
        sy2 = min(image.shape[0] - 1, sy1 + sh + 8)
        if sy2 > sy1 and sx2 > sx1:
            sub_rect = image[sy1:sy2, sx1:sx2]
            stat_bg = np.zeros_like(sub_rect)
            stat_bg[:] = (0, 0, 180) if is_overloaded else (20, 120, 30)
            cv2.addWeighted(sub_rect, 0.25, stat_bg, 0.75, 0, sub_rect)
            cv2.putText(image, sub_text, (sx1 + 5, sy2 - 4), font, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

def process_frame(frame, frame_idx, cap=None):
    """
    Main detection and tracking pipeline:
    - Runs YOLO inference for vehicles, persons, luggage/cargo
    - Maps passengers & cargo to vehicle bounding boxes
    - Tracks vehicles over frames
    - Triggers non-blocking evidence capture and DB recording on violations
    """
    frame_h, frame_w = frame.shape[:2]

    # Store frame in rolling buffer for video clip capture
    with buffer_lock:
        frame_buffer.append(frame.copy())

    annotated = frame.copy()

    # Run YOLO detection
    results = model(frame, verbose=False)[0]

    detections = []
    persons = []
    cargo_items = []

    if results.boxes is not None:
        for box in results.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id].lower()
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            mapped = map_label(label)
            if mapped is not None and conf >= 0.35:
                detections.append(([x1, y1, x2, y2], mapped, conf))

            if label == "person" and conf >= 0.30:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                persons.append((cx, cy, [x1, y1, x2, y2]))

            if label in ("backpack", "suitcase", "handbag", "box", "package") and conf >= 0.25:
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                cargo_items.append((cx, cy))

    # Update tracker
    tracks = tracker.update(detections, frame_idx)

    # Process each tracked vehicle
    for track in tracks:
        x1, y1, x2, y2 = track.bbox
        ex = expand_bbox(track.bbox, pad=25, w=frame_w, h=frame_h)

        # Count passengers whose centroid falls within expanded vehicle area
        pcount = 0
        for cx, cy, pbox in persons:
            if ex[0] <= cx <= ex[2] and ex[1] <= cy <= ex[3]:
                pcount += 1
                # Draw subtle indicator dot on passenger
                cv2.circle(annotated, (cx, cy), 3, (0, 255, 255), -1)

        # For bikes/cars, if no individual person detected inside due to angle, count default 1 driver
        if pcount == 0 and track.label in ("bike", "car", "van", "auto"):
            pcount = 1

        # Estimate cargo weight
        cargo_est = 0
        for cx, cy in cargo_items:
            if ex[0] <= cx <= ex[2] and ex[1] <= cy <= ex[3]:
                cargo_est += 15  # ~15kg per luggage detection
                cv2.circle(annotated, (cx, cy), 3, (255, 200, 0), -1)

        # Evaluate overload rules
        status, reason = check_overload(track.label, pcount, cargo_est)
        is_overloaded = (status == "Overloaded")

        if is_overloaded:
            track.violation_counter += 1
        else:
            track.violation_counter = max(0, track.violation_counter - 1)

        # Header badge label
        label_text = f"#{track.id} {track.label.upper()} | P:{pcount} C:{cargo_est}kg"
        sub_text = f"! OVERLOADED: {reason}" if is_overloaded else "STATUS: OK"

        # Draw HUD overlays
        draw_hud_box(annotated, track.bbox, label_text, is_overloaded=is_overloaded, sub_text=sub_text)

        # Record violation evidence once per vehicle track
        if is_overloaded and track.violation_counter >= 2 and not track.captured:
            prefix = f"{track.label}_id{track.id}"
            photo_rel = save_photo_evidence(annotated, prefix)
            video_rel = save_video_evidence_async(prefix, duration_sec=CAPTURE_SECONDS, fps=CAPTURE_FPS)
            
            insert_overloaded(
                vehicle_type=track.label,
                passengers=pcount,
                cargo_weight=cargo_est,
                violation_reason=reason,
                photo_path=photo_rel,
                video_path=video_rel,
                confidence=track.confidence
            )
            track.captured = True
            track.recorded_violation = True
            print(f"🚨 Overload Violation Logged: Vehicle #{track.id} ({track.label}) - {reason}")

    # Draw Global HUD Banner at top
    banner_h = 36
    overlay = annotated.copy()
    cv2.rectangle(overlay, (0, 0), (frame_w, banner_h), (15, 15, 20), -1)
    cv2.addWeighted(overlay, 0.7, annotated, 0.3, 0, annotated)

    cv2.putText(
        annotated,
        f"AI OVERLOAD MONITOR | Active Tracks: {len(tracks)} | Frame: {frame_idx}",
        (12, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 220, 255),
        1,
        cv2.LINE_AA
    )

    return annotated
