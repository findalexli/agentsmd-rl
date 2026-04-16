FROM node:22-slim

# Install required tools including pytest and patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    patch \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt-get/lists/*

# Install pnpm
RUN npm install -g pnpm

# Create working directory
WORKDIR /workspace

# Clone the repo at the base commit (parent of merge commit)
RUN git clone --filter=blob:none https://github.com/electric-sql/electric.git /workspace/electric \
    && cd /workspace/electric \
    && git checkout deb2a61614678fac029773a56b618382fe5b70f2

# Skip monorepo prepare scripts and install only typescript-client deps
WORKDIR /workspace/electric/packages/typescript-client

# Install dependencies without running lifecycle scripts
RUN pnpm install --ignore-scripts

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir for the task
WORKDIR /workspace/electric
