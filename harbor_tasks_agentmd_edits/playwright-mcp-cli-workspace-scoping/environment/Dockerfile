FROM node:22-slim

# Install Python for test runner and git for cloning
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone Playwright at the base commit (before the fix)
# Using shallow clone for faster checkout
RUN git clone --filter=blob:none --depth=100 https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git checkout 08752e9a9be05e5d11173977c8651cf105c1aace

WORKDIR /workspace/playwright

# Install dependencies (using npm ci for reproducibility)
# This repo has a complex build setup, we only need the mcp/cli parts
RUN npm ci --ignore-scripts || npm install --ignore-scripts

# Build the TypeScript files (lightweight build)
RUN cd packages/playwright && \
    npx tsc --noEmit -p src/mcp/tsconfig.json 2>/dev/null || true

# Ensure log directory exists for Harbor
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
