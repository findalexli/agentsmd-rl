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

# Create workspace
WORKDIR /workspace

# Clone React repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=78f5c504b732aec0eb12514bc2cf3f27a8143dd2
RUN git clone --depth=1 https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/react

# Sanitize: remove git history but keep files
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Install minimal dependencies (just what test.sh needs)
# React already has yarn.lock, install only test dependencies
RUN yarn install --frozen-lockfile --prefer-offline 2>&1 || true

# Create log directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV CI=true
WORKDIR /workspace/react
