# syntax=docker/dockerfile:1
FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up git user
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create workspace
WORKDIR /workspace

# Clone VS Code repo at base commit (pre-fix)
# Using sanitized snapshot (no .git history for smaller size)
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin 67fdb3ee04fbd04430cd47702977eaa51bd14c40 && \
    git checkout 67fdb3ee04fbd04430cd47702977eaa51bd14c40 && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

WORKDIR /workspace/vscode

# Install minimal dependencies for TypeScript parsing
RUN npm ci --ignore-scripts --prefer-offline 2>/dev/null || npm install --ignore-scripts 2>/dev/null || true

# Create log directories
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Verify TypeScript is available
RUN npx tsc --version

CMD ["/bin/bash"]
