"""
レポート生成関連
統計レポートのPDF出力
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from constants import TARGET_ZONES


def export_report_to_pdf(db_path: str, pdf_path: str):
    """統計レポートをPDFとして出力"""
    conn = sqlite3.connect(db_path)

    query = """
        SELECT
            cm.zone_name as Zone,
            ROUND(AVG(cm.adjusted_time_seconds), 1) as Average,
            ROUND(MIN(cm.adjusted_time_seconds), 1) as Shortest,
            ROUND(MAX(cm.adjusted_time_seconds), 1) as Longest,
            zt.target_seconds as Target,
            ROUND((zt.target_seconds / AVG(cm.adjusted_time_seconds)) * 100, 1) as Achievement
        FROM cycle_measurements cm
        LEFT JOIN zone_targets zt ON cm.zone_name = zt.zone_name
        WHERE cm.is_valid = 1
        GROUP BY cm.zone_name
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("⚠️ No data to export to PDF")
        return

    # ゾーン名の順序を指定
    df['Zone'] = pd.Categorical(df['Zone'], categories=TARGET_ZONES, ordered=True)
    df = df.sort_values('Zone')

    # 達成率に応じた評価（○×△）
    def get_status_symbol(achievement):
        if achievement >= 95:
            return '○'
        elif achievement >= 90:
            return '△'
        else:
            return '×'

    df['Status'] = df['Achievement'].apply(get_status_symbol)

    # 単位を追加
    df['Average'] = df['Average'].apply(lambda x: f"{x:.1f}s")
    df['Shortest'] = df['Shortest'].apply(lambda x: f"{x:.1f}s")
    df['Longest'] = df['Longest'].apply(lambda x: f"{x:.1f}s")
    df['Target'] = df['Target'].astype(str) + 's'
    df['Achievement'] = df['Achievement'].astype(str) + '%'

    # シンプルな表作成
    fig, ax = plt.subplots(figsize=(12, len(df) + 1))
    ax.axis('tight')
    ax.axis('off')

    title_text = f'Assembly Performance Report\n{datetime.now().strftime("%Y-%m-%d")}'
    plt.title(title_text, fontsize=16, pad=20, fontweight='bold')

    table = ax.table(cellText=df.values, colLabels=df.columns,
                     cellLoc='center', loc='center',
                     bbox=[0, 0, 1, 1])

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # ヘッダー行のスタイル
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # データ行のスタイル
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            table[(i, j)].set_facecolor('#F0F0F0' if i % 2 == 0 else '#FFFFFF')

    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, bbox_inches='tight', dpi=150)
        plt.close()

    print(f"\n✅ PDF report exported: {pdf_path}")


def generate_all_reports(db_path: str, output_dir: str):
    """統計レポートとCSVを生成"""
    from database import export_cycle_data_csv
    
    print("\n" + "="*80)
    print("📊 Generating Reports")
    print("="*80)

    # 1. LLM用CSV - 全サイクルデータ
    csv_path = f"{output_dir}/cycle_data.csv"
    export_cycle_data_csv(db_path, csv_path)

    # 2. 基本統計レポート（PDF）
    pdf_path = f"{output_dir}/performance_report.pdf"
    export_report_to_pdf(db_path, pdf_path)

    print("\n" + "="*80)
    print("✅ All reports generated successfully")
    print("="*80)