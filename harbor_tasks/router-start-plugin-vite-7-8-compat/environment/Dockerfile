FROM node:22-slim

# Install python3 for pytest
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=5accb6f86de38d62d1daae3aeed8b168ede46b30
RUN git clone --depth 100 --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout ${BASE_COMMIT}

# Install pnpm
RUN npm install -g pnpm

# Install dependencies and build (only what's needed for tests)
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Pre-build the package to ensure dist exists
RUN pnpm nx run @tanstack/start-plugin-core:build

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
