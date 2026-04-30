FROM node:22-slim

# Install Python for test runner and basic tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone playwright repo at base commit
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 8710e613f8297cebe33c4f6a745999ab4e4907aa && \
    git checkout FETCH_HEAD

WORKDIR /workspace/playwright

# Install npm dependencies (needed for TypeScript compilation)
RUN npm ci --ignore-scripts

# Create log directory
RUN mkdir -p /logs/verifier
