# Dockerfile for superset webpack config task
FROM node:22-slim

# Install git, python3 (needed by pytest runner), zstd (for simple-zstd npm pkg), and build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone repo with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset

# Checkout base commit (before the fix)
WORKDIR /workspace/superset
RUN git checkout ed659958f312c89b7f6b6dd0acbb08c850bbd6c3

# Install only superset-frontend dependencies (needed to load webpack.config.js)
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to repo root
WORKDIR /workspace/superset
