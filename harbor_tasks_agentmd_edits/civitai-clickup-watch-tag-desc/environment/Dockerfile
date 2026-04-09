FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/civitai/civitai.git /workspace/civitai && \
    cd /workspace/civitai && \
    git checkout 76f8944088d812aaab4e6780fc742d1d213df287 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/civitai

# Install npm dependencies (required for clickup skill to work)
RUN npm ci --legacy-peer-deps 2>&1 || npm install --legacy-peer-deps 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
