FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG REPO_URL=https://github.com/huggingface/transformers.git
ARG BASE_COMMIT=ade7a05a42bf53b183bb78c181743be063c5ff14
RUN git init transformers \
    && cd transformers \
    && git remote add origin ${REPO_URL} \
    && git -c protocol.version=2 fetch --depth 1 --filter=blob:none origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT} \
    && rm -rf .git

# CPU-only torch + torchvision wheels.
RUN pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.5.1 \
        torchvision==0.20.1

# Pinned deps required by transformers v5 dev branch (matches setup.py constraints).
RUN pip install \
        numpy==1.26.4 \
        regex==2025.10.22 \
        tokenizers==0.22.1 \
        huggingface-hub==1.5.0 \
        pyyaml==6.0.2 \
        safetensors==0.5.2 \
        packaging==24.2 \
        filelock==3.16.1 \
        requests==2.32.3 \
        tqdm==4.67.1 \
        httpx==0.28.1 \
        pydantic==2.10.4 \
        typer==0.15.1 \
        pillow==11.0.0 \
        pytest==8.3.4 \
        pytest-json-report==1.5.0 \
        pytest-metadata==3.1.1 \
        ruff==0.14.10

# timm pulls torch as hard dep; install with --no-deps to keep our CPU torch.
RUN pip install --no-deps timm==1.0.23

RUN pip install --no-deps -e /workspace/transformers

RUN mkdir -p /logs/verifier
