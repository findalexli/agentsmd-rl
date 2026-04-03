FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    tmux \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

ARG BASE_COMMIT=f944b4c5352be02623d2d7415c0806350f875114

# Clone repo and create sanitized snapshot
RUN git clone https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git fetch --depth=1 origin $BASE_COMMIT && \
    git checkout $BASE_COMMIT && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install dependencies for the reconciler package
RUN npm install --legacy-peer-deps 2>&1 | tail -20 || true

# Install minimal test dependencies
RUN cd packages/react-reconciler && npm install --legacy-peer-deps 2>&1 | tail -20 || true

# Set up paths
ENV NODE_ENV=development
RUN mkdir -p /logs/verifier
