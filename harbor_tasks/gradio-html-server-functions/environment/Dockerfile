FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 7c3fa2a6900cfa3c87cb61ffa9b34b75d1ae49ba && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/gradio

ENV PYTHONPATH="/workspace/gradio"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Install gradio and its dependencies so imports work (install the repo in editable mode)
RUN pip install --no-cache-dir pillow numpy pydantic && \
    pip install --no-cache-dir -e /workspace/gradio/client/python && \
    pip install --no-cache-dir -e /workspace/gradio

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
