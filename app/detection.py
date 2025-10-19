"""
物体検出関連
YOLOv8を使った検出とゾーン判定
"""

from typing import List, Dict
from constants import CLASS_NAMES, CONFIDENCE_THRESHOLDS, TARGET_ZONES, STATIC_ZONES


def detect_objects(frame, model):
    """YOLOv8でオブジェクト検出"""
    results = model.predict(frame, imgsz=640, conf=0.10, verbose=False)
    return results


def count_workers(results):
    """フレーム内のWorker数をカウント"""
    worker_count = 0

    for r in results:
        class_ids = r.boxes.cls.cpu().numpy().astype(int)
        confidences = r.boxes.conf.cpu().numpy()

        for class_id, conf in zip(class_ids, confidences):
            if class_id in CONFIDENCE_THRESHOLDS and conf >= CONFIDENCE_THRESHOLDS[class_id]:
                label = CLASS_NAMES.get(class_id, "Unknown")
                if label == "Worker":
                    worker_count += 1

    return worker_count


def check_overlap(box: List[int], zone_coords: List[int]) -> bool:
    """バウンディングボックスとゾーン座標の重なりを確認"""
    bx1, by1, bx2, by2 = box
    zx1, zy1, zx2, zy2 = zone_coords
    is_separated = (bx1 > zx2 or bx2 < zx1 or by1 > zy2 or by2 < zy1)
    return not is_separated


def detect_zone_objects(results):
    """各ゾーン内のオブジェクトを検出"""
    zone_detections = {}

    for zone in TARGET_ZONES:
        zone_detections[zone] = {
            "assembling": False,
            "pallet": False
        }

    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy().astype(int)
        confidences = r.boxes.conf.cpu().numpy()
        class_ids = r.boxes.cls.cpu().numpy().astype(int)

        for box, conf, class_id in zip(boxes, confidences, class_ids):
            if class_id in CONFIDENCE_THRESHOLDS and conf >= CONFIDENCE_THRESHOLDS[class_id]:
                label = CLASS_NAMES.get(class_id, "Unknown")

                for zone in TARGET_ZONES:
                    zone_coords = STATIC_ZONES[zone]
                    if check_overlap(box, zone_coords):
                        if label == "Assembling":
                            zone_detections[zone]["assembling"] = True
                        elif label == "Pallet":
                            zone_detections[zone]["pallet"] = True

    return zone_detections