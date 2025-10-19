"""
動画処理関連
動画の読み込み、書き出し、切り出し
"""

import cv2
from constants import FPS, OUTPUT_DIR, VIDEO_MARGIN_SECONDS, TARGET_ZONES


def open_video(video_path: str):
    """動画ファイルを開く"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error opening video: {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps < 1.0:
        fps = FPS

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"✅ Video opened: {width}x{height} @ {fps}fps ({total_frames} frames)")

    return {
        "cap": cap,
        "fps": fps,
        "width": width,
        "height": height,
        "total_frames": total_frames
    }


def create_video_writer(output_path: str, fps: float, width: int, height: int):
    """動画書き出し用のWriterを作成"""
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    return out


def extract_cycle_video(source_video_path: str, output_path: str, start_time: float, end_time: float, margin: float, fps: float):
    """動画から指定範囲を切り出し"""
    cap = cv2.VideoCapture(source_video_path)
    if not cap.isOpened():
        print(f"❌ Error opening video: {source_video_path}")
        return False

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    extract_start_time = max(0, start_time - margin)
    extract_end_time = min(total_frames / fps, end_time + margin)

    start_frame = int(extract_start_time * fps)
    end_frame = int(extract_end_time * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    current_frame = start_frame

    while current_frame <= end_frame and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()

    duration = extract_end_time - extract_start_time
    print(f"✅ Video extracted: {output_path} (Duration: {duration:.2f}s)")
    return True


def extract_longest_cycle_videos(zone_states: dict, output_video_path: str, fps: float):
    """各ゾーンの最長サイクル動画を切り出し"""
    extracted_videos = []

    for zone in TARGET_ZONES:
        results = zone_states[zone]["results"]

        if len(results) == 0:
            print(f"\n⚠️ [{zone}] No measurement data - skipping video extraction")
            continue

        # 最長サイクルのみ抽出
        longest = max(results, key=lambda x: x['adjusted_time_seconds'])
        longest_output = f"{OUTPUT_DIR}/{zone}_longest_cycle_{longest['cycle_number']}.mp4"
        print(f"\n🔴 [{zone}] Longest cycle #{longest['cycle_number']}: {longest['adjusted_time_seconds']}s")

        extract_cycle_video(
            output_video_path,
            longest_output,
            longest['start_time_sec'],
            longest['end_time_sec'],
            VIDEO_MARGIN_SECONDS,
            fps
        )
        extracted_videos.append(longest_output)

    return extracted_videos