FROM node:22-slim

# Install Python for the test runner and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create working directory
WORKDIR /workspace

# Clone the playwright repo at the base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 703996071cb3a7ec642b30a2b428c369c3ebb7c7

# Install npm dependencies
WORKDIR /workspace/playwright
RUN npm ci

# Build required packages (the runCode.ts imports from playwright-core)
RUN npm run build

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/playwright
