FROM node:22-slim

# Install git, python3 (for pytest runner), patch, and pnpm
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm globally
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone repository at base commit (sparse clone for efficiency)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout d1174179082d896a9674532994a4d6b38238c37e

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build packages (needed for tests to run)
RUN pnpm build:all

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for task execution
WORKDIR /workspace/router
