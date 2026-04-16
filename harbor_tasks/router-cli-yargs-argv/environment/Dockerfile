FROM node:22-slim

# Install pnpm and Python for pytest runner
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g pnpm@10 \
    && pip install pytest --break-system-packages --quiet

# Set working directory
WORKDIR /workspace

# Clone the repo at the base commit
ARG BASE_COMMIT=8d9988a054020f3b3be97dac367cbe81b08fc44a
RUN git clone --filter=blob:none --depth=100 https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Build the router-cli package (needed for testing)
RUN pnpm nx run @tanstack/router-cli:build

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir for tests
WORKDIR /workspace/router
