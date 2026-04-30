FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    USE_HUB_KERNELS=NO

RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates make \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
        torch==2.5.1+cpu --index-url https://download.pytorch.org/whl/cpu

RUN pip install \
        numpy==2.2.1 \
        packaging==24.2 \
        pyyaml==6.0.2 \
        regex==2025.10.23 \
        tokenizers==0.22.1 \
        safetensors==0.5.2 \
        huggingface-hub==1.5.0 \
        tqdm==4.67.1 \
        filelock==3.16.1 \
        requests==2.32.3 \
        typer==0.15.1 \
        httpx==0.28.1 \
        h11==0.16.0 \
        anyio==4.13.0 \
        httpcore==1.0.9 \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        ruff==0.14.10 \
        libcst==1.5.0

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git \
    && cd transformers \
    && git checkout 74a2a4d0c790788a3b65b975510577f8dc6e81d5 \
    && pip install -e . --no-deps

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers
