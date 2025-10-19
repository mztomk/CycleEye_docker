"""
定数定義
すべてのパス、しきい値、設定をここで管理
"""

import os

# ======================
# パス設定
# ======================

# 実行環境を判定（Docker or ローカル）
# Dockerの場合は /app/ に配置される想定
if os.path.exists("/app/data"):
    # Docker環境
    BASE_DIR = "/app"
else:
    # ローカル環境（相対パス）
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# パス設定
MODEL_PATH = os.path.join(BASE_DIR, "data", "models", "best.pt")
VIDEO_PATH = os.path.join(BASE_DIR, "data", "input", "simulation_video.mp4")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
DB_PATH = os.path.join(OUTPUT_DIR, "cycle_time_data.db")
OUTPUT_VIDEO_PATH = os.path.join(OUTPUT_DIR, "result_with_detections.mp4")
PDF_PATH = os.path.join(OUTPUT_DIR, "performance_report.pdf")

# ======================
# YOLOv8 クラス定義
# ======================
CLASS_NAMES = {
    0: "Worker",
    1: "Pallet",
    2: "Assembling"
}

# ======================
# 測定対象ゾーン
# ======================
TARGET_ZONES = ["A_Assemble", "A2_Assemble", "B_Assemble", "B2_Assemble"]

# ======================
# 信頼度しきい値
# ======================
CONFIDENCE_THRESHOLDS = {
    0: 0.40,  # Worker
    1: 0.30,  # Pallet
    2: 0.10,  # Assembling
}

# ======================
# サイクルタイム計測設定
# ======================
FPS = 24.0  # 動画のフレームレート

# ノイズ耐性設定
N_FRAMES_GRACE_START = 1  # 開始判定の連続フレーム数
N_FRAMES_GRACE_STOP = 5   # 終了判定の連続フレーム数

# 時間調整定数
FRAME_DIFFERENCE = N_FRAMES_GRACE_STOP - N_FRAMES_GRACE_START
ADJUSTMENT_SECONDS = FRAME_DIFFERENCE / FPS

# ======================
# 静的ゾーン座標
# ======================
STATIC_ZONES = {
    "A_Assemble": [140, 260, 150, 310],
    "A2_Assemble": [550, 260, 560, 310],
    "B_Assemble": [750, 260, 760, 310],
    "B2_Assemble": [1150, 260, 1160, 310],
    "Zone_A": [25, 375, 565, 540],
    "Zone_B": [635, 375, 1170, 540],
}

# ======================
# 動画切り出し設定
# ======================
VIDEO_MARGIN_SECONDS = 2.0  # 切り出し時の前後マージン