FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/lobehub/lobe-chat.git /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git checkout 918e4a8fa182a564ed5bbb59cf7f3075c3cbce29 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Install minimal deps needed by test_outputs.py (pytest)
RUN pip3 install --break-system-packages --no-cache-dir pytest || pip3 install --no-cache-dir pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
