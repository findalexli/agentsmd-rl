FROM node:22-slim

# Install dependencies for git and python3 (needed by test runner)
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the repo at the base commit
ARG BASE_COMMIT=4df350b1c81b61ea471ff12767efd8e05f773377
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/playwright

# Install npm dependencies (only what we need for testing)
RUN npm ci --ignore-scripts --prefer-offline 2>&1 || npm install --ignore-scripts --prefer-offline 2>&1 || true

# Create test output directory
RUN mkdir -p /logs/verifier
