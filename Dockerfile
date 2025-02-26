# NVIDIA CUDA 11.8 + cuDNN 포함된 Python 3.11 기반 이미지
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# CUDA 및 cuDNN 환경 변수 설정
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# 최신 libstdc++6 설치 (GLIBCXX 문제 해결)
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
    apt-get update && apt-get install -y libstdc++6

# Python 및 패키지 설치
RUN apt-get update && apt-get install -y \
    python3.11 python3-pip python3.11-venv python3.11-dev \
    build-essential libevdev-dev git \
    libcudnn8 libcublas-11-8 libcusolver-11-8 \
    && rm -rf /var/lib/apt/lists/*

# Python 기본 실행 버전 변경
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3

WORKDIR /app

# Python 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 🚀 NumPy 버전 고정 (NumPy 2.0.2 문제 해결)
RUN pip install --no-cache-dir "numpy<2.0.0"

# 🚀 PyTorch + torchvision을 **CUDA 11.8 버전**으로 맞춰서 설치
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cu118 \
    torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118

# 🚀 bitsandbytes를 최신 버전으로 설치 (GPU 지원 버전)
RUN pip uninstall -y bitsandbytes && \
    pip install --no-cache-dir bitsandbytes --upgrade

# 정적 파일 저장 디렉토리 생성 (권한 부여)
RUN mkdir -p /app/staticfiles && chmod 777 /app/staticfiles

# 소스 코드 복사
COPY . /app/

# 환경 변수 설정
COPY .env /app/.env

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


