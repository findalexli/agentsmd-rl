FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace
WORKDIR /workspace

# Clone the Playwright repository at the base commit
# Base commit: 08752e9a9be05e5d11173977c8651cf105c1aace
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git checkout 08752e9a9be05e5d11173977c8651cf105c1aace

# Install dependencies
WORKDIR /workspace/playwright
RUN npm ci

# Build the packages needed for the CLI
WORKDIR /workspace/playwright/packages/playwright
RUN npm run build

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/playwright
