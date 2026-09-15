import cv2
import numpy as np
import os

def create_synthetic_test_video(output_path="sample_traffic.mp4", duration_sec=5, fps=20):
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    for f in range(total_frames):
        # Create road background
        frame = np.full((height, width, 3), (80, 80, 80), dtype=np.uint8)
        # Road lane markings
        cv2.line(frame, (0, height // 2), (width, height // 2), (255, 255, 255), 2)
        
        # Add timestamp text
        cv2.putText(frame, f"Test Video Feed - Frame {f}/{total_frames}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        out.write(frame)

    out.release()
    print(f"Sample video created: {output_path}")

if __name__ == "__main__":
    create_synthetic_test_video()
