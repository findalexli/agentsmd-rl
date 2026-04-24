FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang repo at base commit
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout ef2d4013d77cf1267e032d7a7a745dc3a6f74880 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

ENV PYTHONPATH="/workspace/sglang/python"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pydantic dataclasses numpy

# Verifier output directory
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black codespell isort ruff 2>/dev/null || pip install --no-cache-dir black codespell isort ruff
