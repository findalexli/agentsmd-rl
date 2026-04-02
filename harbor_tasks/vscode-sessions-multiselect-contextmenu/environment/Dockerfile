FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Base commit: parent of merge commit 64e73b0
ARG BASE_COMMIT=0705ebef87428a3a1d38df65b38da286a7b9174c

# Clone VS Code repo at base commit
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot (remove git history, create clean repo)
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@benchmark.ai" && \
    git config user.name "Benchmark Agent" && \
    git commit -m "snapshot"

# Install Node.js dependencies (minimal for type-checking)
RUN cd /workspace/vscode && \
    npm ci --ignore-scripts --legacy-peer-deps 2>&1 | tail -20 || true

# Set environment variables
ENV NODE_ENV=development
ENV PATH="/workspace/vscode/node_modules/.bin:${PATH}"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
