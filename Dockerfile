# NVIDIA CUDA 11.8 + cuDNN 포함된 Python 3.11 기반 이미지
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# CUDA 및 cuDNN 환경 변수 설정
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# 최신 libstdc++6 설치 (GLIBCXX 문제 해결)
RUN mkdir -p /tmp && chmod 1777 /tmp && \
    apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends software-properties-common gnupg2 && \
    add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
    apt-get update --allow-releaseinfo-change && apt-get install -y libstdc++6

# Python 및 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3-pip python3.11-venv python3.11-dev \
    build-essential libevdev-dev git \
    libcudnn8 libcublas-11-8 libcusolver-11-8 \
    && rm -rf /var/lib/apt/lists/*

# Python 기본 실행 버전 변경
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3

WORKDIR /app
# 허깅페이스 캐시 디렉토리 설정
ENV HF_HOME=/app/.cache/huggingface

# Python 패키지 설치
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# 🚀 NumPy 버전 고정 (NumPy 2.0.2 문제 해결)
RUN pip install "numpy<2.0.0"

# 🚀 PyTorch + torchvision을 **CUDA 11.8 버전**으로 맞춰서 설치
RUN pip install --extra-index-url https://download.pytorch.org/whl/cu118 \
    torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118

# 🚀 bitsandbytes 최신 버전으로 설치 (GPU 지원)
RUN pip uninstall -y bitsandbytes && pip install --no-cache-dir bitsandbytes --upgrade

# 정적 파일 저장 디렉토리 생성 (권한 부여)
RUN mkdir -p /app/staticfiles && chmod 777 /app/staticfiles

# 소스 코드 복사
COPY . /app/

# LoRA 어댑터 관련 파일 추가
COPY adapter_config.json /app/
COPY adapter_model.safetensors /app/

# 🚀 config 폴더가 존재하는 경우 강제 복사 (실행 시 확인)
RUN mkdir -p /app/config && \
    if [ -d "/mnt/config" ]; then cp -r /mnt/config/* /app/config/; fi && \
    if [ -d "/mnt/docker/config" ]; then cp -r /mnt/docker/config/* /app/config/; fi

# 환경 변수 설정
COPY .env /app/.env

# 🚀 Python 환경 변수 추가 (config 모듈 인식 가능하도록 설정)
ENV PYTHONPATH="/app:/app/corkagefree"

# 🚀 Django 정적 파일 수집 (bitsandbytes 무시)
RUN python3 manage.py collectstatic --noinput

# Django ASGI 실행 (Daphne 사용)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "corkagefree.asgi:application"]














# FROM python:3.10-slim

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     portaudio19-dev \
#     python3-dev \
#     libasound-dev \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt /app/
# RUN pip install --upgrade pip && pip install -r requirements.txt

# COPY . /app/

# COPY .env /app/.env

# RUN python manage.py collectstatic --noinput

# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "corkagefree.asgi:application"]


