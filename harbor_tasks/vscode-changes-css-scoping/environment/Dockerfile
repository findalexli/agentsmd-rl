FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# VS Code repo at base commit (parent of merge commit b15c078a^ = 96b9755)
ARG BASE_COMMIT=96b97550f6c2316dae1e45be6f3f1ce9364bd99d
RUN git clone --depth=1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "test@test.com" && \
    git config user.name "Test User"

# Configure environment
WORKDIR /workspace/vscode

# Create logs directory for test output
RUN mkdir -p /logs/verifier
