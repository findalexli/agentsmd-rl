FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install pytest
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytest
ENV PATH="/opt/venv/bin:$PATH"

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone the Playwright repo at base commit with shallow depth
RUN git clone --depth=100 --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout a8ea6558c5f28f3e7a7d8a39d52c732053eee6a1

WORKDIR /workspace/playwright

# Install npm dependencies (only production/needed for testing)
RUN npm ci --prefer-offline 2>&1 || npm install 2>&1 || true

# Build the project (required for TypeScript compilation)
RUN npm run build 2>&1 || true

# Set working directory for tests
WORKDIR /workspace/playwright
