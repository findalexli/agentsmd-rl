FROM node:22-slim

# Install required system packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
RUN mkdir -p /workspace/vscode /logs/verifier

# Clone VS Code at the base commit (sanitized snapshot)
ARG BASE_COMMIT=abea71e2b7c1daecf68232d5d2a96efe3a6bc7f0
RUN git clone https://github.com/microsoft/vscode.git /workspace/vscode-src && \
    cd /workspace/vscode-src && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    mv .git /tmp/git-backup && \
    mkdir -p .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    rm -rf /tmp/git-backup

# Install minimal dependencies needed for validation
WORKDIR /workspace/vscode-src
RUN npm ci --legacy-peer-deps --ignore-scripts 2>&1 | tail -20 || true

# Set git user
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace/vscode
RUN ln -s /workspace/vscode-src/* /workspace/vscode/ && \
    ln -s /workspace/vscode-src/.github /workspace/vscode/

ENV NODE_OPTIONS="--max-old-space-size=4096"
