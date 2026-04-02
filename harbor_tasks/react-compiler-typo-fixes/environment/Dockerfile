FROM node:22-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Clone React repository at base commit
WORKDIR /workspace
RUN git clone --depth 1 https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth=1 origin ba833da405d44260e94bd47c13eec90816bf44f1 && \
    git checkout ba833da405d44260e94bd47c13eec90816bf44f1 && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Install compiler dependencies only (minimial)
WORKDIR /workspace/react/compiler
RUN yarn install --frozen-lockfile

# Set working directory
WORKDIR /workspace/react

# Create logs directory
RUN mkdir -p /logs/verifier
