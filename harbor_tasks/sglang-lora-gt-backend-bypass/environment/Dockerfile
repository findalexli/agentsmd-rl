FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none --depth=100 https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout 41c7c97ff30a8f5e969cefc3efac57f0f3fdbb64 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

ENV PYTHONPATH="/workspace/sglang"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
