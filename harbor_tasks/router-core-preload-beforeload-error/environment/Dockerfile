FROM node:22-slim

# Install pnpm and python3 (needed for pytest runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g pnpm@10

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none --single-branch https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 4756d760ca00e290210684fcd23f39e0931ab384

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Build the router-core package (needed for tests)
RUN CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:build

# Setup pytest
RUN python3 -m pip install --break-system-packages pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
