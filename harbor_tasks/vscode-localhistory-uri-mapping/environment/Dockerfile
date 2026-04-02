FROM node:22-slim

# Install system dependencies
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

# Clone VS Code repo at base commit (pre-fix)
WORKDIR /workspace
ARG BASE_COMMIT=8c61afa3677cb13ce3071eac5326312fc4d2193a
RUN git clone --depth 1 https://github.com/microsoft/vscode.git && \
    cd vscode && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/vscode

# Install dependencies (minimized - only what's needed for TypeScript checking)
RUN npm ci --ignore-scripts 2>&1 | tail -20 || npm install --legacy-peer-deps 2>&1 | tail -20

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV PYTHONPATH=/workspace/vscode
