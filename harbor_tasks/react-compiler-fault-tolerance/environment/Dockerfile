FROM node:20-slim

# Install Python and other dependencies needed for testing
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace/react

# Create logs directory for scorer
RUN mkdir -p /logs/verifier

# Install Yarn
RUN corepack enable && corepack prepare yarn@stable --activate

# Clone at the base commit (pre-fix) and create a sanitized snapshot
ARG BASE_COMMIT=9b2d8013eed2b02193aebc37a614b37853ada214
RUN git init && \
    git remote add origin https://github.com/facebook/react.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "snapshot"

# Configure git user for any subsequent git operations
RUN git config --global user.email "agent@example.com" && \
    git config --global user.name "Agent"

# Install compiler dependencies (minimal for testing)
WORKDIR /workspace/react/compiler
RUN yarn install --frozen-lockfile 2>&1 || yarn install 2>&1 || true

WORKDIR /workspace/react
