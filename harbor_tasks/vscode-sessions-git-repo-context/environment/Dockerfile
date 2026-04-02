FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    cpio \
    && rm -rf /var/lib/apt/lists/*

# Clone VS Code repository at the pre-fix commit
WORKDIR /workspace
ARG BASE_COMMIT=b15c078a6d22d9d2fd182d80658e6d9a6a1b8559
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Initialize git for later patch operations (sanitized snapshot)
RUN cd /workspace/vscode && \
    rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/vscode

# Install minimal npm dependencies needed for compilation checking
# Only install what we need for TypeScript validation
RUN npm ci --ignore-scripts --prefer-offline 2>&1 | tail -20 || true

# Build essential parts of the workspace
RUN npm run compile-extensions-build 2>&1 | tail -30 || true

# Create logs directory
RUN mkdir -p /logs/verifier

ENV PATH="/workspace/vscode/node_modules/.bin:${PATH}"
