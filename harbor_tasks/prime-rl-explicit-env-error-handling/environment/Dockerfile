FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout 05165f6c09009c1b2ed3e4c93997152f8cfb6e29 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

ENV PYTHONPATH="/workspace/prime-rl"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir pytest

# Verifier output directory
RUN mkdir -p /logs/verifier
