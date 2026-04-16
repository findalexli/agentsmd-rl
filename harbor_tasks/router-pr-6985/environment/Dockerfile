FROM node:22-slim

# Install dependencies needed for testing
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 5accb6f86de38d62d1daae3aeed8b168ede46b30

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the packages needed for testing
RUN pnpm nx run @tanstack/start-plugin-core:build

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/router
