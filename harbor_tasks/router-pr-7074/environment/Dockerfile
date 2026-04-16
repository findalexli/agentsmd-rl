# TanStack Router benchmark environment
FROM node:22-slim

# Install git, python3 (for pytest runner), and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the repository at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 30835cb8e935b740c92fa95909a073e644dde530

WORKDIR /workspace/router

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the router-plugin package and its dependencies
RUN pnpm nx run @tanstack/router-plugin:build

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["/bin/bash"]
