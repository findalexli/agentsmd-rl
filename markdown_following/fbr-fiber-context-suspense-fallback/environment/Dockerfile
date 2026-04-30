FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone React repo at base commit (before the fix)
WORKDIR /workspace
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin f944b4c5352be02623d2d7415c0806350f875114 && \
    git checkout f944b4c5352be02623d2d7415c0806350f875114

WORKDIR /workspace/react

# Clean up git history and make it a fresh snapshot
RUN rm -rf .git && \
    git init && \
    git config user.email "test@example.com" && \
    git config user.name "Test User" && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies (minimal - yarn should fetch what's needed)
RUN yarn install --frozen-lockfile --network-timeout 100000

# Create test output directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/react
