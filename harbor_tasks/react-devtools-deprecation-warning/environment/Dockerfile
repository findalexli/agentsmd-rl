FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React repo at base commit (parent of merge commit 7b5b561b)
# Base commit: 014138df87869b174956f90a33fd6cf66e160114
ENV REACT_COMMIT=014138df87869b174956f90a33fd6cf66e160114
RUN git clone --depth 1 --no-checkout https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth 1 origin $REACT_COMMIT && \
    git checkout $REACT_COMMIT

WORKDIR /workspace/react

# Sanitize snapshot - remove .git history to create clean state
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent" && \
    git commit -m "snapshot"

# Create necessary directories
RUN mkdir -p /logs/verifier

# Set environment
ENV NODE_ENV=development
ENV CI=true
WORKDIR /workspace/react
