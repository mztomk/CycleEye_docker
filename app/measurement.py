"""
サイクルタイム計測・状態管理
各ゾーンの測定状態を管理し、サイクルを記録
"""

from datetime import datetime
from constants import TARGET_ZONES, N_FRAMES_GRACE_START, N_FRAMES_GRACE_STOP, ADJUSTMENT_SECONDS
from database import save_cycle_to_db


def initialize_zone_states():
    """各ゾーンの状態管理辞書を初期化"""
    zone_states = {}
    for zone in TARGET_ZONES:
        zone_states[zone] = {
            "measuring": False,
            "start_frame": None,
            "start_time_sec": None,
            "start_datetime": None,
            "is_valid_cycle": True,
            "assembling_count": 0,
            "pallet_count": 0,
            "cycle_number": 0,
            "results": []
        }
    return zone_states


def update_zone_state(state: dict, assembling_detected: bool, pallet_detected: bool,
                     current_frame: int, current_time_sec: float, zone: str, db_path: str):
    """1ゾーンの状態を更新し、必要に応じてサイクルを記録"""

    # ================
    # 1. 待機中の処理
    # ================
    if not state["measuring"]:
        # パターンA: パレット（空）検出 → 待機継続
        if pallet_detected:
            state["assembling_count"] = 0
            state["pallet_count"] += 1
            return None

        # パターンB: 組立検出 → 測定開始判定
        elif assembling_detected:
            state["assembling_count"] += 1
            state["pallet_count"] = 0

            # 連続検出が閾値を超えたら測定開始
            if state["assembling_count"] >= N_FRAMES_GRACE_START:
                state["measuring"] = True
                state["start_frame"] = current_frame
                state["start_time_sec"] = current_time_sec
                state["start_datetime"] = datetime.now()
                state["cycle_number"] += 1
                state["is_valid_cycle"] = True
                print(f"🟢 [{zone}] Cycle #{state['cycle_number']} started at {current_time_sec:.2f}s")
            return None

        # パターンC: 何も検出されない → カウントリセット
        else:
            state["assembling_count"] = 0
            state["pallet_count"] = 0
            return None

    # ================
    # 2. 測定中の処理
    # ================
    else:
        # パターンA: 組立継続 → 測定継続
        if assembling_detected:
            state["assembling_count"] += 1
            state["pallet_count"] = 0
            return None

        # パターンB: パレット（完成品）検出 → 測定終了判定
        elif pallet_detected:
            state["pallet_count"] += 1
            state["assembling_count"] = 0

            # 連続検出が閾値を超えたら測定終了
            if state["pallet_count"] >= N_FRAMES_GRACE_STOP:
                state["measuring"] = False
                end_datetime = datetime.now()

                # 時間計算
                elapsed = current_time_sec - state["start_time_sec"]
                adjusted_time = elapsed - ADJUSTMENT_SECONDS

                # 有効なサイクルのみ保存
                if state["is_valid_cycle"]:
                    cycle_data = {
                        "zone_name": zone,
                        "cycle_number": state["cycle_number"],
                        "start_datetime": state["start_datetime"].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "end_datetime": end_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                        "start_frame": state["start_frame"],
                        "end_frame": current_frame,
                        "elapsed_seconds": round(elapsed, 3),
                        "adjusted_time_seconds": round(adjusted_time, 3),
                        "start_time_sec": round(state["start_time_sec"], 2),
                        "end_time_sec": round(current_time_sec, 2)
                    }

                    state["results"].append(cycle_data)
                    save_cycle_to_db(db_path, cycle_data)

                    print(f"🔴 [{zone}] Cycle #{state['cycle_number']} completed: {adjusted_time:.2f}s")
                    return cycle_data
                else:
                    print(f"⚠️ [{zone}] Cycle #{state['cycle_number']} invalidated (3+ workers)")
                    return None

            return None

        # パターンC: 何も検出されない → カウントリセット
        else:
            state["assembling_count"] = 0
            state["pallet_count"] = 0
            return None


def mark_invalid_cycles(zone_states: dict):
    """Worker数が3人以上の場合、測定中の全ゾーンを無効化"""
    for zone in TARGET_ZONES:
        if zone_states[zone]["measuring"]:
            zone_states[zone]["is_valid_cycle"] = False