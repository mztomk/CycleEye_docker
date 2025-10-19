"""
メイン実行スクリプト
4ゾーン並行測定システムのオーケストレーター
"""

import os
import torch
from datetime import datetime
from ultralytics import YOLO

# 自作モジュールのインポート
from constants import (
    MODEL_PATH, VIDEO_PATH, DB_PATH, OUTPUT_DIR, 
    OUTPUT_VIDEO_PATH, FPS
)
from database import init_database, set_zone_targets
from detection import detect_objects, count_workers, detect_zone_objects
from measurement import initialize_zone_states, update_zone_state, mark_invalid_cycles
from drawing import annotate_frame
from video_utils import open_video, create_video_writer, extract_longest_cycle_videos
from report import generate_all_reports


def setup_environment():
    """環境セットアップを実行"""
    init_database(DB_PATH)
    set_zone_targets(DB_PATH, target_seconds=5.0)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR}\n")


def load_model(model_path: str):
    """YOLOv8モデルをロード"""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = YOLO(model_path)
        model.to(device)
        print(f"✅ Model loaded on {device}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {model_path}")
        print(f"Details: {e}")
        return None


def run_measurement_loop(model, video_info: dict, output_video_path: str):
    """測定メインループを実行"""
    cap = video_info["cap"]
    fps = video_info["fps"]
    width = video_info["width"]
    height = video_info["height"]

    out = create_video_writer(output_video_path, fps, width, height)

    zone_states = initialize_zone_states()

    current_frame = 0

    print("\n--- Starting 4-zone parallel measurement ---")
    print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_frame += 1
        current_time_sec = current_frame / fps

        # オブジェクト検出
        results = detect_objects(frame, model)

        # Worker数カウント
        worker_count = count_workers(results)

        # 各ゾーンの検出
        zone_detections = detect_zone_objects(results)

        # Worker数チェック
        if worker_count >= 3:
            mark_invalid_cycles(zone_states)

        # 各ゾーンの状態更新
        from constants import TARGET_ZONES
        for zone in TARGET_ZONES:
            assembling_detected = zone_detections[zone]["assembling"]
            pallet_detected = zone_detections[zone]["pallet"]

            update_zone_state(
                zone_states[zone],
                assembling_detected,
                pallet_detected,
                current_frame,
                current_time_sec,
                zone,
                DB_PATH
            )

        # フレームに描画
        annotate_frame(frame, results, zone_states, worker_count, current_time_sec)

        # 動画に書き込み
        out.write(frame)

    cap.release()
    out.release()

    print(f"\n✅ Video processing completed: {output_video_path}")
    print(f"📅 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return zone_states


def main():
    """
    メイン関数 - 4ゾーン並行測定システムのオーケストレーター

    処理フロー:
    1. 環境セットアップ（DB初期化、フォルダ作成）
    2. モデルと動画のロード
    3. 測定ループの実行
    4. レポート生成
    5. 最長サイクル動画の切り出し
    """

    print("="*80)
    print("🚀 AI Cycle Time Measurement System")
    print("="*80)

    # GPUチェック
    print(f"GPU available: {torch.cuda.is_available()}")

    # 1. 環境セットアップ
    setup_environment()

    # 2. モデルロード
    model = load_model(MODEL_PATH)
    if not model:
        print("❌ Failed to load model. Exiting.")
        return None

    # 3. 動画を開く
    video_info = open_video(VIDEO_PATH)
    if not video_info:
        print("❌ Failed to open video. Exiting.")
        return None

    # 4. 測定ループ実行
    zone_states = run_measurement_loop(model, video_info, OUTPUT_VIDEO_PATH)

    # 5. レポート生成（統計表PDF + CSV）
    generate_all_reports(DB_PATH, OUTPUT_DIR)

    # 6. 最長サイクル動画を切り出し
    print("\n" + "="*70)
    print("🎬 Extracting longest cycle videos for each zone")
    print("="*70)

    extracted_videos = extract_longest_cycle_videos(
        zone_states,
        OUTPUT_VIDEO_PATH,
        video_info["fps"]
    )

    # 7. 完了メッセージ
    print("\n" + "="*80)
    print("✅ All processing completed!")
    print("="*80)
    print(f"📁 Results saved to: {OUTPUT_DIR}")
    print(f"📊 PDF Report: {OUTPUT_DIR}/performance_report.pdf")
    print(f"📄 CSV Data: {OUTPUT_DIR}/cycle_data.csv")
    print(f"🎥 Output Video: {OUTPUT_VIDEO_PATH}")
    print(f"🎬 Extracted Videos: {len(extracted_videos)} files")

    # 8. 全測定結果を返す
    from constants import TARGET_ZONES
    all_results = []
    for zone in TARGET_ZONES:
        all_results.extend(zone_states[zone]["results"])

    return all_results


if __name__ == "__main__":
    main()