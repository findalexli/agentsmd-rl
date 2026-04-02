FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone React repo at base commit (pre-fix)
ARG BASE_COMMIT=3e319a943cff862b8fbb8e96868f9f153a9e199d
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize the snapshot
WORKDIR /workspace/react
RUN rm -rf .git && \
    git init && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies for testing (just what's needed to parse/validate)
RUN yarn install --frozen-lockfile --network-timeout 600000 2>/dev/null || npm install

# Create verifier directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
