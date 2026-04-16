# Base image with Node.js for TanStack Router
FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install pytest in a way that works on Debian
RUN pip install pytest --break-system-packages

# Set up pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Clone the repository at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 576b5acd874f0a7fa11b0cbd8186eb7448268b09

WORKDIR /workspace/router

# Install dependencies (scripts may need some packages)
# Note: We only need minimal deps for the release script
RUN pnpm install --ignore-scripts || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set default shell
SHELL ["/bin/bash", "-c"]
