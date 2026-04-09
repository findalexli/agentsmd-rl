FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential make tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (blob-less clone for speed)
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 28af8184fb00a0e9bc778c3defdec39bbe7e8839 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

ENV PYTHONPATH="/workspace/transformers/src"

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
