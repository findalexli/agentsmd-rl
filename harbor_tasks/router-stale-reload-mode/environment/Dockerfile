FROM node:22-slim

# Install pnpm and python3 (needed by pytest runner)
RUN apt-get update && apt-get install -y python3 python3-pip python3-pytest git curl && \
    npm install -g pnpm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up workspace
WORKDIR /workspace

# Clone the repo at the base commit
ARG BASE_COMMIT=79cd4d5afa22903f94655602d244f83bdc220641
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the router-core package (needed for tests)
RUN CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:build --outputStyle=stream --skipRemoteCache

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment for Nx
ENV CI=1
ENV NX_DAEMON=false
