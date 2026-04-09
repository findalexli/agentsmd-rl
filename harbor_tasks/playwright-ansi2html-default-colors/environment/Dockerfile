FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow to reduce image size for this large monorepo)
RUN git clone --filter=blob:none --no-checkout \
    https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 09a1261b764fc5c106fa8ca1e3c0bee4e8ddb3d1 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# Install tsx for running TypeScript tests directly without full build
RUN npm install -g tsx

WORKDIR /workspace/playwright

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
