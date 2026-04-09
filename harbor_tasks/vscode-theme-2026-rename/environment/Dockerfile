FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git for any patch operations (MUST be before git commit)
RUN git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent"

# Set up workspace
WORKDIR /workspace

# Sanitized snapshot at base commit (parent of merge commit)
RUN git clone --depth=1 https://github.com/microsoft/vscode.git vscode \
    && cd vscode \
    && git fetch --depth=1 origin 573fb0a665c269634b8eb30759b6f2584c0ff127 \
    && git checkout 573fb0a665c269634b8eb30759b6f2584c0ff127 \
    && rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

WORKDIR /workspace/vscode

# Install only minimal dependencies needed for testing
RUN npm install --ignore-scripts 2>&1 | tail -20 || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Install dependencies for build scripts
RUN cd build && npm install --ignore-scripts 2>&1 | tail -20 || true
