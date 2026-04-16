FROM node:22-slim

# Install Python for pytest and required tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the router repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git && \
    cd router && \
    git checkout 49d7cbb7768c085be2ce31b36ef3da272b0ebbdd

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Install playwright for tests
RUN pnpm exec playwright install

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables for sandboxed execution
ENV CI=1
ENV NX_DAEMON=false
