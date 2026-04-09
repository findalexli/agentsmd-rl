FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang repo at base commit
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout ba78f6e0efb925fbb0f99e7f060eb2cb410331df && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install minimal test dependencies
RUN pip install --no-cache-dir numpy pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
