# TanStack Router benchmark environment
FROM node:22-slim

# Install git, python, and patch for test harness
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Clone repository with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router

WORKDIR /workspace/router

# Checkout the base commit (parent of merge commit)
RUN git checkout a0a6aa8b8ad801f0a364b6c27722d5a929c14e70

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the router-core package (needed for tests)
RUN pnpm nx run @tanstack/router-core:build

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
