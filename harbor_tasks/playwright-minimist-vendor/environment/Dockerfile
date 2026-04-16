FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install pytest --break-system-packages

# Create workspace
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone repo at base commit (before the minimist vendor PR)
ARG BASE_COMMIT=4df350b1c81b61ea471ff12767efd8e05f773377
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git repo && \
    cd repo && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/repo

# Install npm dependencies (don't build - that's part of the fix)
RUN npm ci --prefer-offline

# Verify repo structure
RUN ls -la packages/playwright-core/src/tools/cli-client/
