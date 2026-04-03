FROM node:22-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Clone at base commit (sanitized snapshot - no .git history)
ARG BASE_COMMIT=1e3152365df2f7a23a5ad947e83f40914413be16
RUN git init . && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init . && \
    git add -A && \
    git commit -m "snapshot"

# Configure git for any future operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Install dependencies (React uses yarn via corepack)
RUN corepack enable && corepack prepare yarn@1.22.22 --activate
RUN yarn install --frozen-lockfile --network-timeout=600000 || yarn install

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
