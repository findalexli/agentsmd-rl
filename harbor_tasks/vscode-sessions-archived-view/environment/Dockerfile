FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code repo at base commit (pre-fix)
ARG BASE_COMMIT=3d5035e98791181f4fb04962a8a7b127106d2626
RUN git clone --depth=100 https://github.com/microsoft/vscode.git vscode \
    && cd vscode \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT} \
    && rm -rf .git

# Re-initialize git for clean state
RUN cd vscode \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

# Install minimal dependencies (TypeScript compilation only)
RUN cd vscode && npm ci --ignore-scripts 2>&1 | tail -20 || true

# Configure git
RUN git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent"

# Set working directory
WORKDIR /workspace/vscode

# Create verifier logs directory
RUN mkdir -p /logs/verifier
