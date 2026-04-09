FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout a35f5896e43d2585d9206e8256b4d7e321fcd0fe && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

# Install all gradio dependencies
RUN pip install -e . 2>/dev/null || true

# Tests import from gradio.node_server
ENV PYTHONPATH="/workspace/gradio"

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
