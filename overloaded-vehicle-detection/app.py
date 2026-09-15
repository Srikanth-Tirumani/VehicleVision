# app.py
import sys
import argparse
import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import CAMERA_SOURCE
from my_utils.detector import process_frame
from my_utils.database import init_db

def get_capture(source):
    if isinstance(source, str) and source.isdigit():
        source = int(source)

    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(source)
    else:
        video_path = source
        if not os.path.isabs(video_path):
            video_path = os.path.join(BASE_DIR, video_path)
        cap = cv2.VideoCapture(video_path if os.path.exists(video_path) else source)
    return cap

def main():
    init_db()
    parser = argparse.ArgumentParser(description="AI Overloaded Vehicle Detection")
    parser.add_argument(
        "--source",
        default=CAMERA_SOURCE,
        help="Camera index (e.g. 0) or path to video file (e.g. traffic_demo.mp4) or RTSP URL"
    )
    args = parser.parse_args()
    source = args.source

    cap = get_capture(source)

    if not cap.isOpened():
        print("=" * 60)
        print(f"❌ Error: Cannot open video/camera source: {source}")
        print("=" * 60)
        print("Reasons & Solutions:")
        print("1. No webcam is connected or camera access is disabled in Windows Settings.")
        print("2. To test with a video file, run:")
        print("   python app.py --source traffic_demo.mp4")
        print("=" * 60)
        return

    frame_idx = 0
    print("=" * 60)
    print(f"✅ AI Overload Detection Engine Active on source: {source}")
    print("👉 Live window active. Press 'q' or ESC inside the window to quit.")
    print("=" * 60)

    delay = 1 if isinstance(source, int) else 25

    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop video file if reaching end
            if isinstance(source, str) and not source.isdigit():
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break
            else:
                break

        frame_idx += 1
        annotated = process_frame(frame, frame_idx, cap)

        cv2.imshow("Overload Guardian AI - Live Monitor", annotated)
        key = cv2.waitKey(delay) & 0xFF
        if key in (ord('q'), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Detection stopped.")

if __name__ == "__main__":
    main()
