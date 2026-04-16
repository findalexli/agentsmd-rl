FROM node:22-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 4ea461ec27defe24f6b70a4c6fc402d48561de9a

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the solid-router package (and dependencies)
RUN pnpm nx run @tanstack/solid-router:build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/router
