# ベースイメージ: Python 3.10 (軽量版)
FROM python:3.10-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なライブラリをインストール
# OpenCVの依存関係を解決
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Pythonライブラリの依存関係をコピー
COPY app/requirements.txt .

# Pythonライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ .

# データディレクトリを作成
RUN mkdir -p /app/data/input /app/data/models /app/data/output

# デフォルトコマンド
CMD ["python", "main.py"]