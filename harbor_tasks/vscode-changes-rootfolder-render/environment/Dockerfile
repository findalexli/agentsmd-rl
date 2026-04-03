# VS Code Changes View - File Tree Rendering Improvements
# Base: post-fix commit parent

FROM node:22-slim

# Install dependencies for VS Code build
RUN apt-get update && apt-get install -y \
    git curl ca-certificates build-essential \
    python3 python3-pip \
    pkg-config libsecret-1-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone VS Code at the base commit (pre-fix)
ARG REPO_URL=https://github.com/microsoft/vscode.git
ARG BASE_COMMIT=3c51a00d738294aa6e113b87e38b8ea770fbf9ee

RUN git clone --depth=1 --no-checkout --filter=blob:none "$REPO_URL" vscode
WORKDIR /workspace/vscode
RUN git fetch --depth=1 origin "$BASE_COMMIT" && \
    git checkout "$BASE_COMMIT"

# Sanitize repository - create clean history-less snapshot
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for TypeScript checking
RUN npm ci --cache /tmp/npm-cache --prefer-offline 2>&1 | tail -20 || \
    npm ci --no-audit --prefer-offline --legacy-peer-deps 2>&1 | tail -20

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_OPTIONS="--max-old-space-size=8192"
WORKDIR /workspace/vscode
