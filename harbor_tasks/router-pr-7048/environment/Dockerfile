FROM node:22-slim

# Install git, python3 (needed by pytest runner), and patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Enable corepack for pnpm
RUN corepack enable

WORKDIR /workspace

# Clone repository with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router

# Checkout base commit (parent of merge commit)
RUN git checkout a1ab2646348cb9fa89c98b2128a65d992925014f

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the router-generator package and its dependencies
RUN pnpm nx run @tanstack/router-generator:build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
