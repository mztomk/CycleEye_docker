"""
データベース操作関連
SQLiteを使った計測データの保存・集計
"""

import sqlite3
import pandas as pd
from datetime import datetime
from constants import TARGET_ZONES


def init_database(db_path: str):
    """データベースとテーブルを初期化"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cycle_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_name TEXT NOT NULL,
            cycle_number INTEGER NOT NULL,
            start_datetime TEXT NOT NULL,
            end_datetime TEXT NOT NULL,
            start_frame INTEGER,
            end_frame INTEGER,
            elapsed_seconds REAL NOT NULL,
            adjusted_time_seconds REAL NOT NULL,
            is_valid BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS zone_targets (
            zone_name TEXT PRIMARY KEY,
            target_seconds REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


def clear_database(db_path: str):
    """データベースの全データを削除（テーブル構造は維持）"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM cycle_measurements")
    cursor.execute("DELETE FROM zone_targets")
    
    conn.commit()
    conn.close()
    print("✅ Database cleared (all data deleted)")


def set_zone_targets(db_path: str, target_seconds: float = 5.0):
    """各ゾーンの目標時間を設定"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for zone in TARGET_ZONES:
        cursor.execute("""
            INSERT OR REPLACE INTO zone_targets (zone_name, target_seconds)
            VALUES (?, ?)
        """, (zone, target_seconds))

    conn.commit()
    conn.close()
    print(f"✅ Target time set: {target_seconds}s for all zones")


def save_cycle_to_db(db_path: str, cycle_data: dict):
    """1サイクルのデータをデータベースに保存"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cycle_measurements (
            zone_name, cycle_number, start_datetime, end_datetime,
            start_frame, end_frame, elapsed_seconds, adjusted_time_seconds,
            is_valid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cycle_data['zone_name'],
        cycle_data['cycle_number'],
        cycle_data['start_datetime'],
        cycle_data['end_datetime'],
        cycle_data['start_frame'],
        cycle_data['end_frame'],
        cycle_data['elapsed_seconds'],
        cycle_data['adjusted_time_seconds'],
        1
    ))

    conn.commit()
    conn.close()


def export_cycle_data_csv(db_path: str, output_path: str):
    """LLM分析用に全サイクルデータをCSVエクスポート"""
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            zone_name,
            cycle_number,
            start_datetime,
            end_datetime,
            start_frame,
            end_frame,
            elapsed_seconds,
            adjusted_time_seconds,
            created_at
        FROM cycle_measurements
        WHERE is_valid = 1
        ORDER BY zone_name, cycle_number
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    df.to_csv(output_path, index=False)
    print(f"\n✅ Cycle data CSV exported: {output_path} ({len(df)} records)")

    return df