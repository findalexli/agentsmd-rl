FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Clone repo at base commit
RUN git init /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git remote add origin https://github.com/lobehub/lobe-chat.git && \
    git fetch --depth=1 origin 08572d060270afd65fcc5efdf7cde9e5fb0b0e04 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat

# Install resend SDK using pnpm (required for import verification)
RUN pnpm add resend 2>/dev/null || true

# Set NODE_PATH to find installed modules
ENV NODE_PATH=/workspace/lobe-chat/node_modules

# Install pytest for test runner
RUN pip3 install --break-system-packages pytest pytest-json-ctrf 2>/dev/null || \
    python3 -m pip install -q pytest pytest-json-ctrf

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
