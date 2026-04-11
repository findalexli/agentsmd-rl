FROM node:22-slim

# Install Python and utilities needed for testing
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

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone React repo at the base commit (pre-fix)
ARG BASE_COMMIT=4b568a8dbb4cb84b0067f353b9c0bec1ddb61d8e
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Sanitize snapshot (remove .git history, re-init)
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Install minimal dependencies (only what tests need)
# React monorepo uses yarn and link: protocol which npm doesn't handle properly
RUN yarn install --frozen-lockfile 2>&1 | tail -20 || true
