FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN npm install -g pnpm@10

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/cloudflare/workers-sdk.git workers-sdk
WORKDIR /workspace/workers-sdk
RUN git checkout 5ededb5d52f4362ce8f72d442ba825d48dcabbf8

# Install dependencies
RUN pnpm install

# Build only the packages we need for testing
RUN pnpm run build --filter wrangler --filter @cloudflare/containers-shared

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/workers-sdk
