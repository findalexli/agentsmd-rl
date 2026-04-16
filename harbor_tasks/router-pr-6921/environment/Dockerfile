FROM node:22-slim

# Install git, curl, and python3 with pytest (needed by test harness)
RUN apt-get update && apt-get install -y git curl python3 python3-pip python3-pytest && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 79cd4d5afa22903f94655602d244f83bdc220641

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the router-core package (needed for tests)
RUN pnpm nx run @tanstack/router-core:build

# Create log directory for verifier
RUN mkdir -p /logs/verifier

ENV CI=1
ENV NX_DAEMON=false
