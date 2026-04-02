FROM node:22-slim

# Install essential tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React repo at base commit
ARG BASE_COMMIT=10680271fab565e0edf948d3a6dc9d30e83df94c
RUN git clone https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/react

# Install dependencies (only what's needed for Flow)
RUN yarn install --frozen-lockfile 2>/dev/null || yarn install

# Sanitize git history for snapshot
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Configure git user for potential patch operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
