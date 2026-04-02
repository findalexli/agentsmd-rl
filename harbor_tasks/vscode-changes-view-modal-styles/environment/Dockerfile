FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /workspace

# Clone VS Code repo at base commit (sanitized snapshot)
ARG BASE_COMMIT=00356ebc69d09b93830f05eb4eabf872d425abdd
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies (minimal - only what's needed for validation)
WORKDIR /workspace/vscode
RUN npm ci --ignore-scripts 2>&1 | tail -20

# Environment setup
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vscode
