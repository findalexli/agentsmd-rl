FROM node:22-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set up workspace
WORKDIR /workspace

# Clone VS Code at the pre-fix base commit
ARG BASE_COMMIT=33250873ecbd4047cd2e29b0f04ae0e7284aa342
RUN git clone --depth 1 https://github.com/microsoft/vscode.git vscode && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/vscode

# Sanitize snapshot (remove .git history but keep files)
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot at base commit"

# Install minimal dependencies for TypeScript type checking
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
WORKDIR /workspace/vscode
