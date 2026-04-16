FROM node:22-slim

# Install git and python3 for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python dependency management
RUN pip3 install uv

WORKDIR /workspace

# Clone the playwright repo at the base commit (shallow clone for speed)
ARG BASE_COMMIT=1ed53ac99ec225a5fc0aacb762a18e3195c61a6c
RUN git clone --depth=1 --filter=blob:none \
    https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install npm dependencies (needed for type checking)
WORKDIR /workspace/playwright
RUN npm ci --prefer-offline --no-audit --no-fund 2>&1 || npm install --prefer-offline --no-audit --no-fund 2>&1 || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/playwright
