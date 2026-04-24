FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout d64f8688833cd73648a1b06932f1fbec542694e3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/AReaL

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages pre-commit ruff 2>/dev/null || pip install --no-cache-dir pre-commit ruff
