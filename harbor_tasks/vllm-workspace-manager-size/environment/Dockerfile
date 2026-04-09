FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Install torch CPU-only (needed to import vllm.v1.worker.workspace)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout 062f1a2d706cfb631521461f6a7ad533cf69a4a8 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vllm

ENV PYTHONPATH="/workspace/vllm"

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
