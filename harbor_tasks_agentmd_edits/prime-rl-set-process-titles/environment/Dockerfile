FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git checkout 8304f1e2acdd9a5264a323f15d132bb7f2015a9f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prime-rl

ENV PYTHONPATH="/workspace/prime-rl"

# Install minimal deps needed by test_outputs.py
RUN pip install --no-cache-dir 'setproctitle>=1.3.0'

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
