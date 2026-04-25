# TanStack Router - Remove global file route helpers task
FROM node:22-slim

# Install python3 for pytest runner, git, and patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.28.0 --activate

# Create workspace and logs directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone repository with filter for efficiency
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

# Checkout the base commit
WORKDIR /workspace/router
RUN git checkout 1f41bc531d28cde6f8deea57ee72aa8949728209

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the relevant packages (react-router and solid-router depend on router-core)
RUN pnpm nx run @tanstack/router-core:build --skipRemoteCache && \
    pnpm nx run @tanstack/react-router:build --skipRemoteCache && \
    pnpm nx run @tanstack/solid-router:build --skipRemoteCache

WORKDIR /workspace/router
