FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Set up git user for snapshot
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

WORKDIR /workspace

# Base commit (parent of merge commit c9ff56ec)
ARG BASE_COMMIT=3ce1316b05968d2a8cffe42a110f2726f2c44c3e

# Clone React repo and create sanitized snapshot
RUN git clone --depth=50 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

WORKDIR /workspace/react

# Install only the minimal dependencies needed for testing DevTools feature flags
# The flag files are simple JS modules, no build needed
RUN npm install --legacy-peer-deps 2>/dev/null || yarn install --frozen-lockfile 2>/dev/null || true

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV CI=true
