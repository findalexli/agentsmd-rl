# React DevTools suspense boundary tracking fix
# Task: react-devtools-markers-dedup
FROM node:22-slim

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

# Clone React at base commit (pre-fix)
ARG BASE_COMMIT=70890e7c58abccef35a6498f7ee702d608be79d6
RUN git clone --depth=1 https://github.com/facebook/react.git react && \
    cd react && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Create sanitized snapshot (no .git history for agent)
RUN cd react && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot" && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Install dependencies (minimal)
RUN cd react && yarn install --frozen-lockfile

# Set up git config
RUN cd react && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# Create log directories
RUN mkdir -p /logs/verifier /logs/agent

WORKDIR /workspace/react
