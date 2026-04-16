FROM node:20-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Enable corepack for yarn/pnpm support
RUN corepack enable

# Set up working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install frontend dependencies
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root for tests
WORKDIR /workspace/superset
