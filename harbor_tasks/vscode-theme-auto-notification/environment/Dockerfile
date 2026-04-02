FROM node:22-slim

# Install required packages including Python for test scoring
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone VS Code repo at base commit
ARG BASE_COMMIT=af50a47c13e23e0b3c46719dbd92fe00144362a5
RUN git clone --depth 1 https://github.com/microsoft/vscode.git /workspace/vscode && \
    cd /workspace/vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot (remove .git history to reduce size)
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "test@test.com" && \
    git config user.name "Test User" && \
    git commit -m "snapshot"

# Set up test infrastructure
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode

# Expose port if needed for testing
EXPOSE 3000
