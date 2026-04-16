# TanStack Router task environment
FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --break-system-packages pytest

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /workspace

# Clone repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 773c7c9cb9c17646020286a2d8721e2f0b628f8c

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the package that contains the sitemap code
RUN pnpm nx run @tanstack/start-plugin-core:build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment for testing
ENV CI=1
ENV NX_DAEMON=false
