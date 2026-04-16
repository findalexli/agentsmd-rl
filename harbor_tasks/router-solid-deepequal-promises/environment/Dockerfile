FROM node:22-slim

# Install pnpm and python3 (needed for pytest runner)
RUN npm install -g pnpm@9 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install pytest

ENV PATH="/opt/venv/bin:$PATH"

# Clone the repo at the base commit (parent of merge commit)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git && \
    cd router && \
    git checkout 4ea461ec27defe24f6b70a4c6fc402d48561de9a

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install --frozen-lockfile

# Build the required packages (core deps first)
ENV CI=1
ENV NX_DAEMON=false
RUN pnpm nx run @tanstack/router-core:build && \
    pnpm nx run @tanstack/solid-router:build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
