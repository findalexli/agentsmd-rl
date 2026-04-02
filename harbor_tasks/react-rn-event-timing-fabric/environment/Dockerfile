FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    tmux \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Clone repo at base commit (detached, no history for smaller image)
ARG BASE_COMMIT=aac12ce597b49093a5add54b00deee3d8980f874
RUN git clone --depth=1 https://github.com/facebook/react.git . \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Sanitize snapshot (no .git history)
RUN rm -rf .git \
    && git init \
    && git add -A \
    && git commit -m "snapshot"

# Install minimal dependencies (just what we need for testing - no build)
RUN yarn install --frozen-lockfile --ignore-scripts 2>/dev/null || yarn install --frozen-lockfile

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Set environment
ENV NODE_ENV=test
ENV PYTHONPATH=/workspace/react

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/react
