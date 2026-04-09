FROM node:22-slim

# Install Python for pytest and basic tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest globally
RUN pip3 install pytest --break-system-packages

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the router repository at base commit
ARG BASE_COMMIT=0e0a2817c30011829a4fefbb7d3bdef1e710d3ef
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout ${BASE_COMMIT}

# Install dependencies and build packages
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile
RUN pnpm build:all

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
