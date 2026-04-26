FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pytest for testing
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    pip3 install pytest pytest-json-ctrf

# Install pnpm
RUN npm install -g pnpm

# Clone repo at base commit (blob-less clone for large monorepo)
RUN git init /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git remote add origin https://github.com/lobehub/lobe-chat.git && \
    git fetch --depth=1 origin 17544558908a97902ef5bf1f564254288f0cf649 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Install npm dependencies using pnpm (needed for linting, testing)
RUN pnpm install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
