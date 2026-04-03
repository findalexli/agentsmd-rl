FROM node:22-slim

# Install system dependencies including Python for test scoring
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git user (required for repo operations)
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Sanitized snapshot: fetch specific commit, remove .git history, re-init
WORKDIR /tmp
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin 9c0323e2cf9be543d6eaa44419598af56922603f && \
    git checkout FETCH_HEAD && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies (Flow is used for type checking)
# React uses yarn for package management
RUN corepack enable && yarn install --frozen-lockfile

# Create workspace directory
RUN mkdir -p /workspace/react && cp -r . /workspace/react/ && \
    mkdir -p /logs/verifier

WORKDIR /workspace/react

# Set up node_modules/.bin in PATH for yarn scripts
ENV PATH="/workspace/react/node_modules/.bin:${PATH}"
