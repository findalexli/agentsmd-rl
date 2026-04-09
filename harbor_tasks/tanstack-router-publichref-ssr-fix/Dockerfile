FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Install pnpm globally
RUN npm install -g pnpm

# Create workspace and logs directories
WORKDIR /workspace
RUN mkdir -p /logs/verifier

# Clone the repository at the base commit (shallow clone for speed)
ARG BASE_COMMIT=7b9faaeee045b018240cb29304c4cae207ce4e57
RUN git clone --filter=blob:none --depth=50 https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ${BASE_COMMIT}

# Install dependencies (using pnpm in the monorepo)
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Build the router-core package (needed for testing)
RUN pnpm nx run @tanstack/router-core:build

# Set working directory for the task
WORKDIR /workspace
