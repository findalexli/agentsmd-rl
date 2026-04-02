# syntax=docker/dockerfile:1
FROM node:22-slim

# Install dependencies needed for building VS Code
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    libx11-dev \
    libxkbfile-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code at the base commit (pre-fix)
# Using depth=1 for size, then sanitizing
ARG BASE_COMMIT=3d91bf7907bba3f8f511a70ba352b2006c7b653a
RUN git clone --depth=1 https://github.com/microsoft/vscode.git vscode \
    && cd vscode \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT} \
    && rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot at base commit"

# Install VS Code npm dependencies (lightweight - just what's needed to compile)
RUN cd /workspace/vscode && npm install --ignore-scripts

# Configure git
RUN git config --global user.email "agent@claude.test" \
    && git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode

# Build type checker only (no need to bundle)
RUN npm run compile-check-ts-native 2>&1 | tail -20 || true
