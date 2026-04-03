FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace

# Clone vscode repo at the pre-fix commit (shallow clone for speed)
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin cc967ecb5526e1e7e4fd5f4cc6e5be60f4947104 && \
    git checkout cc967ecb5526e1e7e4fd5f4cc6e5be60f4947104

WORKDIR /workspace/vscode

# Sanitize snapshot: remove git history and re-initialize
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Install minimal dependencies for TypeScript checking
# VS Code has a complex build, but we only need type checking
type_checking only
RUN npm ci --ignore-scripts --prefer-offline 2>&1 || npm install --legacy-peer-deps 2>&1 || true

ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN mkdir -p /logs/verifier
