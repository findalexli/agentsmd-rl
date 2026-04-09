FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout 57e76686346beeaaec4010ebefc56b9949686457 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime"

# Install CPU-only torch + mbridge + safetensors for test_outputs.py
RUN pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir mbridge safetensors

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
