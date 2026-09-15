# my_utils/tracker.py
import numpy as np

def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    boxAArea = max(0, boxA[2] - boxA[0]) * max(0, boxA[3] - boxA[1])
    boxBArea = max(0, boxB[2] - boxB[0]) * max(0, boxB[3] - boxB[1])
    union = boxAArea + boxBArea - interArea
    return interArea / union if union > 0 else 0.0

class Track:
    def __init__(self, tid, bbox, label, frame_idx, confidence=0.0):
        self.id = tid
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.label = label
        self.last_seen = frame_idx
        self.misses = 0
        self.confidence = confidence
        self.captured = False  # Flag if evidence (photo/video) was already recorded
        self.violation_counter = 0  # Consecutive frames detected as overloaded
        self.recorded_violation = False

class SimpleTracker:
    def __init__(self, iou_thresh=0.25, max_misses=12):
        self.tracks = {}
        self.next_id = 1
        self.iou_thresh = iou_thresh
        self.max_misses = max_misses

    def update(self, detections, frame_idx):
        """
        detections: list of tuples (bbox, label, confidence)
        bbox = [x1, y1, x2, y2]
        """
        matched = set()
        for det in detections:
            if len(det) == 3:
                det_bbox, det_label, det_conf = det
            else:
                det_bbox, det_label = det
                det_conf = 0.8

            best_id = None
            best_iou = 0.0
            for tid, track in self.tracks.items():
                if track.label != det_label:
                    continue
                val = iou(track.bbox, det_bbox)
                if val > best_iou and val >= self.iou_thresh:
                    best_iou = val
                    best_id = tid

            if best_id is not None:
                t = self.tracks[best_id]
                t.bbox = det_bbox
                t.confidence = det_conf
                t.last_seen = frame_idx
                t.misses = 0
                matched.add(best_id)
            else:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = Track(tid, det_bbox, det_label, frame_idx, det_conf)
                matched.add(tid)

        # Increment misses and delete stale tracks
        for tid in list(self.tracks.keys()):
            track = self.tracks[tid]
            if track.last_seen != frame_idx:
                track.misses += 1
                if track.misses > self.max_misses:
                    del self.tracks[tid]

        return list(self.tracks.values())
