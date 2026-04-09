FROM node:22-slim

# Install Python for pytest and required tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit with minimal history
ARG REPO=https://github.com/TanStack/router.git
ARG BASE_COMMIT=a556afa0f07c551cc0edaf17fa7d0de7014a1c68
RUN git clone --filter=blob:none --depth=50 $REPO router && \
    cd router && \
    git checkout $BASE_COMMIT

# Install pnpm
RUN npm install -g pnpm

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Build the router-core package (needed for tests)
RUN pnpm nx run @tanstack/router-core:build

# Create logs directory
RUN mkdir -p /logs/verifier

# Set default working directory
WORKDIR /workspace/router
