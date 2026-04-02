FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Install TypeScript globally for type checking
RUN npm install -g typescript@5.4.5

ARG BASE_COMMIT=76258864c3a7669bd0254946543fe317959d1960

WORKDIR /workspace

# Clone and create sanitized snapshot (no git history needed for test)
RUN git clone --depth=1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

WORKDIR /workspace/vscode

# Install minimal dependencies for running tests (lightweight)
RUN npm ci --prefer-offline --no-audit --progress=false 2>&1 | tail -20 || true

# Pre-compile base TypeScript to catch any pre-existing errors
RUN npm run compile-check-ts-native 2>&1 | tail -30 || true

RUN mkdir -p /logs/verifier

ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV HOME=/tmp
