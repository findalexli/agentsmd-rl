FROM node:22-slim

# Install git, python3 (for pytest runner), and other essentials
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@9

WORKDIR /workspace

# Clone repo with blobless filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git tanstack-router

WORKDIR /workspace/tanstack-router

# Checkout base commit (parent of merge commit)
RUN git checkout 3bc18d4623459a56ae972de8ff969ebf7a994ca7

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the specific package we're testing
RUN pnpm nx run @tanstack/start-plugin-core:build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/tanstack-router
