FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace/vllm && \
    cd /workspace/vllm && \
    git checkout 156405d243924fbede2d4360494a81dea7203334 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/vllm

ENV PYTHONPATH="/workspace/vllm"
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
