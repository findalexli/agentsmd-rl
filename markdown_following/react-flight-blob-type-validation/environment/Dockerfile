FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React repo at base commit (parent of merge commit)
ENV REPO_COMMIT=c80a07509582daadf275f36ffe7a88c3b12e9db4
RUN git clone --depth=1 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin ${REPO_COMMIT} && \
    git checkout ${REPO_COMMIT}

# Sanitize: remove .git history but keep an initialized repo for applying patches
RUN cd /workspace/react && \
    rm -rf .git && \
    git init && \
    git config user.email "test@example.com" && \
    git config user.name "Test User" && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies needed for tests
WORKDIR /workspace/react
RUN yarn install --frozen-lockfile

# Create verifier log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
