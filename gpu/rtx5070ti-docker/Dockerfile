# Dockerfile for ML/AI Development with GPU Support (Blackwell-friendly)
FROM nvidia/cuda:12.8.0-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    wget \
    curl \
    vim \
    htop \
    nvtop \
    && rm -rf /var/lib/apt/lists/*

# Fix for Ubuntu 24.04 externally managed Python environment
RUN pip3 install --break-system-packages --upgrade pip setuptools wheel

# ✅ RTX 5070 Ti (Blackwell sm_120) fix: install latest PyTorch with CUDA 12.4+ support
# Use nightly builds which include sm_120 support for RTX 50 series
RUN pip3 install --break-system-packages --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/nightly/cu124

RUN pip3 install --break-system-packages --no-cache-dir \
    transformers \
    accelerate \
    sentencepiece \
    protobuf \
    huggingface_hub \
    datasets \
    jupyter \
    ipython \
    psutil \
    gputil \
    nvidia-ml-py3

WORKDIR /workspace
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Set environment variables for CUDA debugging and RTX 5070 Ti support
ENV CUDA_LAUNCH_BLOCKING=1
ENV TORCH_CUDA_ARCH_LIST="5.0;6.0;7.0;7.5;8.0;8.6;9.0;12.0"
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

CMD ["bash"]
