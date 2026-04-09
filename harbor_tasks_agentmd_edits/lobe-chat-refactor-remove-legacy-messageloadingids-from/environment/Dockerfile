FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (PR #13662 base)
RUN git clone --filter=blob:none https://github.com/lobehub/lobe-chat.git /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git checkout 034c7c203b23926b09ebe228e19f0567ac729568 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Pre-fetch npm deps for faster test runs
RUN npm ci --legacy-peer-deps 2>&1 || npm install 2>&1 || true

# Install minimal deps needed by test_outputs.py
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    pip3 install pytest pytest-json-ctrf 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
