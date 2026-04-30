FROM node:22-slim

# Install Python for pytest runner and other dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt-get/lists/*

# Install pnpm globally
RUN npm install -g pnpm

# Create workspace directories
RUN mkdir -p /workspace/router /logs/verifier

WORKDIR /workspace

# Clone the repository at the base commit (before the fix)
# Using filter=blob:none for faster clone
RUN git init /workspace/router && \
    cd /workspace/router && \
    git remote add origin https://github.com/TanStack/router.git && \
    git fetch --depth=1 origin 77ad7925d4a6ea88ecd523ca7445ca192ce7a91a && \
    git checkout FETCH_HEAD

# Install dependencies and build all packages in the monorepo first
WORKDIR /workspace/router
RUN pnpm install

# Build all packages in the monorepo to ensure dependencies exist
RUN pnpm run build:all 2>&1 || true

# Test files (test.sh, solve.sh) are mounted at runtime by Harbor, not at build time.
# Removed the build-time chmod since the files don't exist in the build context.

WORKDIR /workspace/router
