FROM node:22-slim

# Install python3, pytest, patch for test runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-pytest git patch \
    && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the router repo at base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git && \
    cd router && \
    git reset --hard d1174179082d896a9674532994a4d6b38238c37e

# Install pnpm globally
RUN npm install -g pnpm

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Build packages needed for testing
RUN pnpm build:all

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
