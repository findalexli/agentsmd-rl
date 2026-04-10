FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Configure git globally first (needed for commit)
RUN git config --global user.email "dev@example.com" && \
    git config --global user.name "Developer"

# Clone React repo at base commit (pre-fix)
# Base commit: c0c37063e2cd8976d839998573012d48d303ada0 (parent of merge)
RUN git clone --no-checkout --depth 1 https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin c0c37063e2cd8976d839998573012d48d303ada0 && \
    git checkout c0c37063e2cd8976d839998573012d48d303ada0

# Sanitize snapshot (remove .git history)
RUN cd /workspace/react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install minimal dependencies (yarn is included in node:22-slim)
WORKDIR /workspace/react
RUN yarn install --frozen-lockfile --network-timeout 600000

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
