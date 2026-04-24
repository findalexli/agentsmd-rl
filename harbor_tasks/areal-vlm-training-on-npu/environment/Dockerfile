FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout b942ed019df2c66b851c397c0836fd31a3787b70 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/AReaL

# Install deps needed by test_outputs.py
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
