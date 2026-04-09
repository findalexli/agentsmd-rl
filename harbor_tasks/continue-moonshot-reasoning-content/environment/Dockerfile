FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT
RUN git clone --filter=blob:none --depth=100 https://github.com/continuedev/continue.git /workspace/continue \
    && cd /workspace/continue \
    && git checkout ${BASE_COMMIT}

# Install core dependencies for testing
WORKDIR /workspace/continue/core
RUN npm install --legacy-peer-deps 2>/dev/null || npm install --force

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
