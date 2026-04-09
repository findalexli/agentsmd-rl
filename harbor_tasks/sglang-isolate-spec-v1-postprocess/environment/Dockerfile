FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (use --filter=blob:none for large monorepos)
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout 106baedbfb9fb18e96e95963b12473a6d21c0ece && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir numpy

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
