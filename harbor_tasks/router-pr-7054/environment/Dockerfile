# TanStack Router - SSR OnRendered script removal benchmark task
FROM node:22-slim

# Install Python3 (required by pytest runner) and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Clone the repository with sparse checkout for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

# Checkout the base commit (before the fix)
WORKDIR /workspace/router
RUN git checkout 0e0a2817c30011829a4fefbb7d3bdef1e710d3ef

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build only the packages needed for testing
RUN pnpm nx run @tanstack/react-router:build --skip-nx-cache
RUN pnpm nx run @tanstack/solid-router:build --skip-nx-cache

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
