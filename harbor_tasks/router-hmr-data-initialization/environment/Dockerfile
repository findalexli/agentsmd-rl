FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
# Using depth to limit size, but we need the base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git fetch --depth=1 origin 30835cb8e935b740c92fa95909a073e644dde530 && \
    git checkout 30835cb8e935b740c92fa95909a073e644dde530

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Build the router-plugin package (and its dependencies)
# This is needed for the tests to work
RUN CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-plugin:build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory back to /workspace/router for tests
WORKDIR /workspace/router
