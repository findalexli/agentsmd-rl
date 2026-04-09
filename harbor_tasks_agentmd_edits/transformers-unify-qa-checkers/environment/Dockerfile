FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential make && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large repo)
RUN git clone --depth=100 https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 28af8184fb00a0e9bc778c3defdec39bbe7e8839 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

ENV PYTHONPATH="/workspace/transformers/src"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir tomli

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
