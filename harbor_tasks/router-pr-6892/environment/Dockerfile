FROM node:22-slim

# Install git, python3 (needed by pytest runner), and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone repository with blobless filter
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

WORKDIR /workspace/router

# Checkout base commit (before the fix)
RUN git checkout 870cf28066954b17e551c4e0f6627e382f0d6a57

# Install dependencies (skip postinstall scripts that might fail)
RUN pnpm install --ignore-scripts || true

# Create logs directory
RUN mkdir -p /logs/verifier
