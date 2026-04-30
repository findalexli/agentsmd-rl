FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git \
    && cd transformers \
    && git checkout 26bb358ea971aebe30729f8a7ae4f3f0fedb1d5a

WORKDIR /workspace/transformers

RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu \
        torch==2.5.1+cpu

RUN pip install \
        "huggingface-hub==1.12.0" \
        "numpy==1.26.4" \
        "packaging==24.2" \
        "pyyaml==6.0.2" \
        "regex==2025.10.22" \
        "tokenizers==0.22.2" \
        "typer==0.12.5" \
        "safetensors==0.4.5" \
        "tqdm==4.67.1" \
        "filelock==3.16.1" \
        "requests==2.32.3" \
        "pytest==8.3.4" \
        "pytest-xdist==3.8.0" \
        "parameterized==0.9.0"

RUN pip install -e . --no-deps

RUN mkdir -p /logs/verifier
