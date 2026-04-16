FROM node:22-slim

# Install system dependencies including python for pytest runner
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 4756d760ca00e290210684fcd23f39e0931ab384

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the packages (needed for tests)
RUN pnpm build:all

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
