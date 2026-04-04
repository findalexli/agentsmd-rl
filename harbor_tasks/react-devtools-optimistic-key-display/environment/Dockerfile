FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone React repo at the pre-fix commit
WORKDIR /workspace
RUN git clone --filter=blob:none --depth=1000 https://github.com/facebook/react.git react

WORKDIR /workspace/react

# Checkout base commit and clean git history (sanitized snapshot)
ARG BASE_COMMIT=57b79b0388b755096216b2b5308113e54eac3be8
RUN git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git -c user.email="agent@example.com" -c user.name="Agent" commit -m "snapshot"

# Install minimal dependencies
RUN npm install --legacy-peer-deps 2>&1 || yarn install 2>&1 || true

# Configure git for any future operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Create logs directory
RUN mkdir -p /logs/verifier
