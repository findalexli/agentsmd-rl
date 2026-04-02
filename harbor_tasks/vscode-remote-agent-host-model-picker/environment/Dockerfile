FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone vscode repo at the base commit
ARG BASE_COMMIT=de413b282f0b15a6618a15a79d4680b720ef9dc8
RUN git clone --depth=1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize: remove .git history to avoid accidental inspection
RUN cd vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for TypeScript compilation
RUN cd vscode && npm install --legacy-peer-deps 2>/dev/null || npm install

# Set up logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
