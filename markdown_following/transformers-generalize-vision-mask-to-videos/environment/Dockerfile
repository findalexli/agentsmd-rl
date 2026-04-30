FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        make \
        build-essential \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch from pytorch index. Pinned for reproducibility.
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1

# Test harness deps. Pinned. ruff is needed because the repo's CLAUDE.md mandates `make style`.
RUN pip install \
        pytest==8.3.4 \
        pytest-json-ctrf==0.3.5 \
        ruff==0.13.0 \
        pyyaml==6.0.2 \
        GitPython==3.1.48

WORKDIR /workspace

# Shallow clone of transformers at the base commit (parent of merge commit ade7a05a42bf53b183bb78c181743be063c5ff14).
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 538368903c6ecdc5f489a8eed4ce809e58fdafb5 && \
    git checkout FETCH_HEAD

# Install transformers in editable mode (no extras — pulls only base deps).
WORKDIR /workspace/transformers
RUN pip install -e .

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers
