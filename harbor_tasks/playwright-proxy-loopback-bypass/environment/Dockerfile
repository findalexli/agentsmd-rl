FROM node:22-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone Playwright repo at base commit (pre-fix)
# Using shallow clone with blob filter for efficiency
RUN git init /workspace/playwright && \
    cd /workspace/playwright && \
    git remote add origin https://github.com/microsoft/playwright.git && \
    git fetch --depth=1 origin 23b12474a184466c5a83db49b7bcf4d45e970a26 && \
    git checkout FETCH_HEAD

# Install minimal dependencies needed for testing
WORKDIR /workspace/playwright
RUN npm ci --ignore-scripts 2>&1 | tail -20 || true

# Install only playwright-core dependencies (the package being modified)
WORKDIR /workspace/playwright/packages/playwright-core
RUN npm ci --ignore-scripts 2>&1 | tail -10 || true

# Create logs directory for reward file
RUN mkdir -p /logs/verifier

WORKDIR /workspace/playwright
