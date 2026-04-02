FROM node:22-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone React repo at base commit (pre-fix)
ARG BASE_COMMIT=c0060cf2a695d719152c939cfc3cced8f7da3e52
RUN git clone --depth 1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Set working directory to compiler
WORKDIR /workspace/react/compiler

# Install dependencies
RUN yarn install --frozen-lockfile

# Configure git
RUN git config --global user.email "test@example.com" && \
    git config --global user.name "Test User"

# Create logs directory
RUN mkdir -p /logs/verifier

# Default working directory for tests
WORKDIR /workspace/react
