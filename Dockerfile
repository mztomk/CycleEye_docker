# ベースイメージ: CUDA環境
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 作業ディレクトリを設定
WORKDIR /app

# Pythonと必要なシステムパッケージを一括インストール
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && ln -s /usr/bin/python3 /usr/bin/python \
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