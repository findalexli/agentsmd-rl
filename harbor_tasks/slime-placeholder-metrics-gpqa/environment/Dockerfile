FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ARG REPO_URL=https://github.com/THUDM/slime.git
ARG BASE_COMMIT=5996c6881e484fe0985ff3c8b8c8ce1af4e32632

RUN git clone --depth=1 --filter=blob:none "$REPO_URL" /workspace/slime && \
    cd /workspace/slime && \
    git checkout "$BASE_COMMIT"

# No heavy deps needed — tests use pure Python (gpqa.py) and AST inspection
# for files that import ray/torch.

ENV PYTHONPATH=/workspace/slime
RUN pip install --no-cache-dir aiohttp pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
