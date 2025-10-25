"""
描画関連
検出結果やゾーン情報をフレームに描画
"""

import cv2
from typing import List, Dict
from constants import CLASS_NAMES, CONFIDENCE_THRESHOLDS, TARGET_ZONES, STATIC_ZONES


def draw_detections(frame, results):
    """検出結果をフレームに描画"""
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy().astype(int)
        confidences = r.boxes.conf.cpu().numpy()
        class_ids = r.boxes.cls.cpu().numpy().astype(int)

        for box, conf, class_id in zip(boxes, confidences, class_ids):
            if class_id in CONFIDENCE_THRESHOLDS and conf >= CONFIDENCE_THRESHOLDS[class_id]:
                label = CLASS_NAMES.get(class_id, "Unknown")

                x1, y1, x2, y2 = box
                box_color = (0, 255, 0)
                thickness = 1
                if label == "Assembling":
                    box_color = (255, 0, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
                text = f"{label} {conf:.2f}"
                if label == "Worker":
                    cv2.putText(frame, text, (x1, y2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, thickness)
                else:
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, thickness)




def draw_static_zones(frame, static_zones: Dict[str, List[int]]):
    """静的ゾーンを破線で描画"""
    for zone_name, coords in static_zones.items():
        x1, y1, x2, y2 = coords
        color = (0, 0, 255)
        thickness = 1
        dash_length = 10

        for x in range(x1, x2, dash_length * 2):
            cv2.line(frame, (x, y1), (min(x + dash_length, x2), y1), color, thickness)
            cv2.line(frame, (x, y2), (min(x + dash_length, x2), y2), color, thickness)
        for y in range(y1, y2, dash_length * 2):
            cv2.line(frame, (x1, y), (x1, min(y + dash_length, y2)), color, thickness)
            cv2.line(frame, (x2, y), (x2, min(y + dash_length, y2)), color, thickness)

        cv2.putText(frame, zone_name, (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)


def draw_zone_status(frame, zone_name: str, zone_coords: List[int], measuring: bool, elapsed_time: float, is_valid: bool):
    """各ゾーンの測定状態を描画"""
    x1, y1, x2, y2 = zone_coords

    text_x = x1 - 20
    text_y = y1 - 50

    status_text = f"{zone_name}:"
    status_color = (0, 255, 255) if measuring else (150, 150, 150)
    cv2.putText(frame, status_text, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

    if measuring:
        time_text = f"Time: {elapsed_time:.2f}s"
        cv2.putText(frame, time_text, (text_x, text_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        if not is_valid:
            warning_text = "No scoring"
            cv2.putText(frame, warning_text, (text_x + 200, text_y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


def draw_all_zone_statuses(frame, zone_states: dict, current_time_sec: float):
    """全ゾーンの状態を描画"""
    for zone in TARGET_ZONES:
        state = zone_states[zone]
        zone_coords = STATIC_ZONES[zone]
        elapsed_time = 0

        if state["measuring"]:
            elapsed_time = current_time_sec - state["start_time_sec"]

        draw_zone_status(frame, zone, zone_coords, state["measuring"],
                        elapsed_time, state["is_valid_cycle"])


def draw_worker_count(frame, worker_count: int):
    """Worker数を描画"""
    worker_text = f"Workers: {worker_count}"
    cv2.putText(frame, worker_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)


def annotate_frame(frame, results, zone_states: dict, worker_count: int, current_time_sec: float):
    """フレームに全ての情報を描画"""
    draw_detections(frame, results)
    draw_static_zones(frame, STATIC_ZONES)
    draw_all_zone_statuses(frame, zone_states, current_time_sec)
    draw_worker_count(frame, worker_count)