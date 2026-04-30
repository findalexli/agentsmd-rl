FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth 1 origin a1ee76cfe1c0fbb4511d5bc2d2fc28622728121c && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

# Minimal deps for testing (no torch/GPU)
RUN pip install --no-cache-dir pillow transformers

ENV PYTHONPATH=/workspace/slime
RUN git config user.name "agent" && git config user.email "agent@test.com"

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages isort ruff 2>/dev/null || pip install --no-cache-dir isort ruff
