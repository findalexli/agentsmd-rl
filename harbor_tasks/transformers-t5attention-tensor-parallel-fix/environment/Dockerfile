FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers repo at base commit
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 38593c2e83964079576eb646fe9b68cce16114dc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

# Install minimal dependencies for testing (no torch needed for our shape tests)
RUN pip install --no-cache-dir numpy pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
