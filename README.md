# CycleEye - AI サイクルタイム計測システム

YOLOv8を使った組立作業の自動サイクルタイム計測システム（Docker対応）

## 📋 目次

- [概要]
- [機能]
- [必要な環境]
- [セットアップ]
- [使い方]
- [出力ファイル]
- [トラブルシューティング]

---

## 📖 概要

このシステムは、製造現場の組立作業を動画から自動分析し、各ゾーンのサイクルタイムを計測します。

**主な特徴:**
- 🤖 YOLOv8による高精度な物体検出
- 🔄 4ゾーン並行測定
- 📊 自動レポート生成（PDF・CSV）
- 🎥 最長サイクル動画の自動抽出
- 🐳 Docker対応（環境構築不要）

---

## ✨ 機能

### 検出対象
- **Worker**: 作業者
- **Pallet**: パレット（空/完成品）
- **Assembling**: 組立中の状態

### 測定ゾーン
- `A_Assemble`
- `A2_Assemble`
- `B_Assemble`
- `B2_Assemble`

### 出力
- 📊 統計レポート（PDF）
- 📄 サイクルデータ（CSV）
- 🎥 検出結果付き動画
- 🎬 各ゾーンの最長サイクル動画

---

## 💻 必要な環境

### Docker使用の場合（推奨）
- Docker Desktop
- メモリ: 4GB以上推奨

### ローカル実行の場合
- Python 3.10以上
- 必要なライブラリ（requirements.txt参照）

---

## 🔧 セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd CycleEye_docker
```

### 2. データファイルの配置

以下のファイルを配置してください：

```
data/
├── input/
│   └── simulation_video.mp4    # 分析対象の動画
└── models/
    └── best.pt                 # YOLOv8学習済みモデル
```

---

## 🚀 使い方

### 方法1: Docker使用（推奨）

#### 初回のみ: イメージをビルド

```bash
docker compose build
```

#### 実行

```bash
docker compose up
```

処理完了後、`data/output/` フォルダに結果が保存されます。

---

### 方法2: ローカル実行

#### 仮想環境の作成

```bash
python3 -m venv env
source env/bin/activate  # Macの場合
# env\Scripts\activate   # Windowsの場合
```

#### ライブラリのインストール

```bash
cd app
pip install -r requirements.txt
```

#### 実行

```bash
python main.py
# または
python3 main.py
```

---

## 📦 出力ファイル

実行完了後、`data/output/` に以下のファイルが生成されます：

| ファイル名 | 内容 |
|-----------|------|
| `performance_report.pdf` | 各ゾーンの統計レポート（平均・最短・最長・達成率） |
| `cycle_data.csv` | 全サイクルの詳細データ（LLM分析用） |
| `result_with_detections.mp4` | 検出結果を描画した全体動画 |
| `cycle_time_data.db` | SQLiteデータベース |
| `A_Assemble_longest_cycle_X.mp4` | A_Assembleゾーンの最長サイクル動画 |
| `A2_Assemble_longest_cycle_X.mp4` | A2_Assembleゾーンの最長サイクル動画 |
| `B_Assemble_longest_cycle_X.mp4` | B_Assembleゾーンの最長サイクル動画 |
| `B2_Assemble_longest_cycle_X.mp4` | B2_Assembleゾーンの最長サイクル動画 |

---

## ⚙️ 設定のカスタマイズ

### constants.py の主な設定項目

```python
# 動画のフレームレート
FPS = 24.0

# 信頼度しきい値
CONFIDENCE_THRESHOLDS = {
    0: 0.40,  # Worker
    1: 0.30,  # Pallet
    2: 0.10,  # Assembling
}

# 測定開始/終了の安定化フレーム数
N_FRAMES_GRACE_START = 1  # 開始判定
N_FRAMES_GRACE_STOP = 5   # 終了判定
```

### 目標時間の変更

`database.py` の `set_zone_targets()` 関数で設定：

```python
set_zone_targets(DB_PATH, target_seconds=5.0)  # デフォルト: 5秒
```

---

## 🐛 トラブルシューティング

### Docker関連

#### エラー: `Cannot connect to the Docker daemon`
**原因:** Docker Desktopが起動していない  
**対処:** Docker Desktopを起動してから再実行

#### エラー: `no space left on device`
**原因:** Dockerのディスク容量不足  
**対処:** Docker Desktopの設定でディスク容量を増やす

---

### ファイル関連

#### エラー: `FileNotFoundError: simulation_video.mp4`
**原因:** 動画ファイルが配置されていない  
**対処:** `data/input/` に動画ファイルを配置

#### エラー: `FileNotFoundError: best.pt`
**原因:** モデルファイルが配置されていない  
**対処:** `data/models/` にモデルファイルを配置

---

### パフォーマンス

#### 処理が遅い
**原因:** CPU環境での実行  
**対処:**
- GPU環境での実行を推奨
- 動画の解像度を下げる
- 短い動画でテストする

---

## 📂 プロジェクト構成

```
CycleEye_docker/
├── app/
│   ├── main.py              # メイン実行スクリプト
│   ├── constants.py         # 定数定義
│   ├── database.py          # DB操作
│   ├── detection.py         # 物体検出
│   ├── measurement.py       # サイクルタイム測定
│   ├── drawing.py           # 描画処理
│   ├── video_utils.py       # 動画処理
│   ├── report.py            # レポート生成
│   └── requirements.txt     # 必要なライブラリ
├── data/
│   ├── input/               # 入力動画
│   ├── models/              # YOLOモデル
│   └── output/              # 出力結果
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

---

## 📝 ライセンス

このプロジェクトは独自のライセンスの下で提供されています。

---

## 👥 作成者

開発・設計: あなたの名前

---

## 📧 お問い合わせ

質問や問題がある場合は、Issue を作成してください。

[def]: #概要
[def2]: #セットアップ