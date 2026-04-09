FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git checkout 52801ff20c3d48ef594912bae3f2e49fbabe0a71 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir torch numpy pytest transformers

ENV PYTHONPATH="/workspace/sglang/python"

# Verifier output directory
RUN mkdir -p /logs/verifier
