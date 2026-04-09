FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/inclusionAI/AReaL.git /workspace/areal && \
    cd /workspace/areal && \
    git checkout cca5b865b0883f7f6cdb02a01d4929387585d20d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/areal

# Install only dataclasses and typing deps needed for test
RUN pip install --no-cache-dir pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
