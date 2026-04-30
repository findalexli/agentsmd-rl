FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Install gradio in editable mode (needed for tests to import)
RUN pip install --no-cache-dir -e . 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
