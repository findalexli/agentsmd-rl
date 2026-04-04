# React Flight CSP eval function name task
FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git user early (needed for snapshot commit)
RUN git config --global user.email "test@example.com" && \
    git config --global user.name "Test User"

# Set up workspace
WORKDIR /workspace/react

# Clone React repo at base commit (pre-fix) and create sanitized snapshot
ARG BASE_COMMIT=87ae75b33f71eb673c55ddb3a147a9e58b7d05bd
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin $BASE_COMMIT && \
    git checkout $BASE_COMMIT && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install dependencies (runs yarn install in the monorepo)
RUN yarn install --frozen-lockfile --network-timeout 100000

# Set up logging directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
