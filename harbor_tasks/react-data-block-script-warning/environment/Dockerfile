FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Set working directory
WORKDIR /workspace

# Clone React repo at base commit (pre-fix)
ARG BASE_COMMIT=4cc5b7a90bac7e1f8ac51a9ac570d3ada3bddcb3
RUN git clone --depth=1 https://github.com/facebook/react.git && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/react

# Install dependencies (minimal for testing)
RUN yarn install --frozen-lockfile

# Sanitize: remove git history but keep source
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Setup for testing
RUN mkdir -p /logs/verifier

# Environment variable for test
ENV CI=true
WORKDIR /workspace/react
