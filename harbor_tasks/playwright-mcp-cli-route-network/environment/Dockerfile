FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages

WORKDIR /workspace

# Clone the Playwright repository at the base commit
# Using depth=1 since we only need the specific commit
RUN git clone --depth=100 --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 824f63da57edf990c6eeab6301d5f1b65dcb4ca8

WORKDIR /workspace/playwright

# Install dependencies
RUN npm ci --no-progress 2>&1 | tail -20

# Build the project (needed for TypeScript compilation)
RUN npm run build 2>&1 | tail -30 || true

# Create logs directory for Harbor
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/playwright
