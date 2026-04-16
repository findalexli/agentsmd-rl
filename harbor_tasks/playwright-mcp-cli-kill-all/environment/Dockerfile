FROM node:22-slim

# Install Python and git for testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace
WORKDIR /workspace

# Clone Playwright repo at base commit (shallow clone for speed)
RUN git clone --depth=100 --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 7aaffc87da20df44d19cf6114efb44a5c99de106

WORKDIR /workspace/playwright

# Install npm dependencies (needed for TypeScript compilation)
RUN npm ci --silent || npm install --silent

# Create logs directory for Harbor
RUN mkdir -p /logs/verifier
