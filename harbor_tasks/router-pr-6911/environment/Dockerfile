FROM node:22-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install --break-system-packages pytest

# Clone repository with filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router

WORKDIR /workspace/router

# Checkout the base commit (parent of merge commit)
RUN git checkout 49d7cbb7768c085be2ce31b36ef3da272b0ebbdd

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the packages needed for solid-router tests
RUN pnpm nx run @tanstack/router-core:build
RUN pnpm nx run @tanstack/history:build
RUN pnpm nx run @tanstack/solid-router:build

# Create logs directory
RUN mkdir -p /logs/verifier
