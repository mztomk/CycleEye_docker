# CycleEye - AI サイクルタイム計測システム

製造現場の組立作業を自動計測する AI システム（プロトタイプ）

---

## 🎯 プロジェクト概要

### 現場の課題

1. **計測の非効率性**
   - サイクルタイム計測が手動で時間がかかる
   - 人的コストが高い

2. **改善活動の障壁**
   - 工程改善を実施しても効果検証が困難
   - 人力計測による誤差で正確な評価ができない
   - 改善のモチベーション維持が難しい

3. **AI導入の遅れ**
   - 現場へのAI導入が進んでいない

### 本システムによる解決

**自動計測の実現**
- YOLOv8による高精度な自動検出
- 4ゾーン並行測定で効率化
- 人的コストの削減

**データの見える化**
- 統計レポートで改善効果を定量評価
- 異常値を自動検出し改善ポイントを提示
- 改善活動へのモチベーション向上

**DX化の橋渡し**
- 小規模な成功体験でAI導入効果を実感
- 現場の心理的ハードルを下げる

### 成果
- AWS GPU環境での実行確認済み
- 正確な検出と計測精度を達成
- 現場目線での実装

---

## 🛠️ 使用技術

| 分野 | 技術 |
|------|------|
| AI/ML | YOLOv8, PyTorch |
| 言語 | Python 3.10 |
| インフラ | Docker, AWS EC2 (g4dn.xlarge) |
| GPU | NVIDIA Tesla T4, CUDA 11.8 |

---

## 📊 システム機能

### 検出対象
YOLOv8による自動検出
- Worker（作業者）
- Pallet（パレット）
- Assembling（組立中の状態）

### 測定ゾーン
4つの組立ゾーンを並行測定
- A_Assemble / A2_Assemble
- B_Assemble / B2_Assemble

### 出力
- 統計レポート（PDF）
- サイクルデータ（CSV）
- 検出結果付き動画
- 最長サイクル動画（各ゾーン）

**LLM分析との連携:**
出力されたCSVデータは、別途開発したLLM自動分析アプリ（Streamlit + GPT-4o）で分析可能。AI による改善提案まで自動化。

---

## 🚀 実行方法

### ローカル環境（CPU）

```bash
# 1. リポジトリクローン
git clone https://github.com/mztomk/CycleEye_docker.git
cd CycleEye_docker

# 2. データ配置
# data/input/simulation_video.mp4
# data/models/best.pt

# 3. docker-compose.yml のGPU設定をコメントアウト
# deploy.resources.reservations.devices の4行を # でコメント化
#   devices:
#     - driver: nvidia
#       count: all
#       capabilities: [gpu]

# 4. 実行
docker compose build
docker compose up
```

### AWS GPU環境

```bash
# EC2 (g4dn.xlarge) で実行
# GPU認識確認
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# 実行
docker compose up
```

**実行デモ動画:** [リンク]

---

## 📁 プロジェクト構成

```
CycleEye_docker/
├── app/              # アプリケーションコード
│   ├── main.py
│   ├── detection.py  # YOLOv8 検出
│   ├── measurement.py # サイクルタイム測定
│   └── ...
├── data/
│   ├── input/        # 入力動画
│   ├── models/       # YOLOモデル
│   └── output/       # 結果
├── Dockerfile        # GPU対応
└── docker-compose.yml
```

---

## 📈 開発背景

**製造現場での実体験から課題を発見**

現場で作業しながら「サイクルタイム計測が手動で大変」「改善活動を行った際の正確な効果検証が困難」という課題に気づき、独学で AI 技術を習得し、プロトタイプを開発しました。

**現場目線での設計:**
- 実用性を重視した検出精度
- 複数ゾーン並行測定
- 異常値の自動検出

---

## 🔗 関連プロジェクト

**CycleEye LLM Analysis**
- Streamlit + GPT-4o による分析アプリ
- サイクルデータを AI が分析・改善提案
- [デモURL]

---

## 📞 お問い合わせ

ご質問・ご相談はお気軽にどうぞ

GitHub: [mztomk](https://github.com/mztomk)