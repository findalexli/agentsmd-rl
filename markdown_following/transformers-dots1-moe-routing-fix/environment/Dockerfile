FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN mkdir -p /workspace/transformers && \
    cd /workspace/transformers && \
    git init -q && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth 1 -q origin 628c54c23d73cf2bf04816e9168d41deb33b1a2f && \
    git checkout -q FETCH_HEAD && \
    git config user.email "task@local" && \
    git config user.name "task" && \
    git branch -f main HEAD && \
    git checkout -q main

RUN pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.4.1+cpu

RUN pip install \
        pytest==8.3.4 \
        libcst==1.5.0 \
        ruff==0.11.7

WORKDIR /workspace/transformers

# Install transformers (editable) with its real dependency closure.
# --no-build-isolation keeps the image small (reuses already-installed wheels for build).
RUN pip install -e . --no-build-isolation

RUN mkdir -p /logs/verifier
