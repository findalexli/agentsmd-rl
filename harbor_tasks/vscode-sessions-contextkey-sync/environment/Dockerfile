FROM node:22-slim

# Install dependencies and Python for scoring
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    bc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone vscode repo at base commit (pre-fix)
# Base commit: 2924b6cf31bca9a2296af760209a088907def726 (parent of merge commit)
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin 2924b6cf31bca9a2296af760209a088907def726 && \
    git checkout 2924b6cf31bca9a2296af760209a088907def726

# Install npm dependencies (needed for compilation checks)
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts 2>&1 || npm install --ignore-scripts 2>&1 || true

# Create sanitized snapshot (no .git history for agent)
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
