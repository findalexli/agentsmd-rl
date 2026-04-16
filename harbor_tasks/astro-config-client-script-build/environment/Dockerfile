FROM node:22-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@latest

# Enable corepack for pnpm
RUN corepack enable pnpm

# Set working directory
WORKDIR /workspace

# Clone the Astro repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=fdd2c5a2f0eb63332b018df01b2c1eb0d5c8a102
RUN git clone --filter=blob:none https://github.com/withastro/astro.git astro && \
    cd astro && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install dependencies and build
WORKDIR /workspace/astro
RUN pnpm install
RUN pnpm run build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default workdir for tests
WORKDIR /workspace/astro
