FROM node:22-slim

# Install git and python3 (needed for tests)
RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone playwright repo at base commit (before the fix)
ARG BASE_COMMIT=a8ea6558c5f28f3e7a7d8a39d52c732053eee6a1
RUN git clone --filter=blob:none --depth=50 https://github.com/microsoft/playwright.git && \
    cd playwright && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/playwright

# Install dependencies (needed for TypeScript compilation checks)
RUN npm ci --silent 2>&1 | tail -5 || npm install --silent 2>&1 | tail -5

# Pre-build to cache
RUN npm run build 2>&1 | tail -10 || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
