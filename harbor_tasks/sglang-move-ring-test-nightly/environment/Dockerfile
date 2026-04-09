FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout 233f3e31bfec68c77c17066b7b270380e773da6b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Set PYTHONPATH for sglang imports
ENV PYTHONPATH="/workspace/sglang/python:/workspace/sglang/test"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Verifier output directory
RUN mkdir -p /logs/verifier
