FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux jq && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (monorepo, use --filter=blob:none)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 46761a321042e8ac1863f4cfc8d73d527956e181 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Install minimal deps needed by test_outputs.py
RUN pip3 install --no-cache-dir pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
