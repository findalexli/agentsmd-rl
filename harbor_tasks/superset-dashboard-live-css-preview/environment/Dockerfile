FROM node:20-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Enable corepack for npm
RUN corepack enable

# Set up working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=4fae5758d5ca210615686e9252a39c88f635c9fb
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps 2>/dev/null || npm install --legacy-peer-deps 2>/dev/null || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root for tests
WORKDIR /workspace/superset
