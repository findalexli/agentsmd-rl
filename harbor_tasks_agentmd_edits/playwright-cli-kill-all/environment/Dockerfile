FROM node:22-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone playwright repo at base commit (shallow clone for speed)
# Base commit: 7aaffc87da20df44d19cf6114efb44a5c99de106
RUN git clone --depth 1 --filter=blob:none https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git fetch --depth=1 origin 7aaffc87da20df44d19cf6114efb44a5c99de106 && \
    git checkout 7aaffc87da20df44d19cf6114efb44a5c99de106

# Install npm dependencies
WORKDIR /workspace/playwright
RUN npm ci

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/playwright
