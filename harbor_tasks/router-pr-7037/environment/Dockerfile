# TanStack Router benchmark task environment
FROM node:22-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Install pnpm
RUN npm install -g pnpm@9

# Clone the repository with sparse checkout for efficiency
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router

# Checkout the base commit (parent of merge commit)
WORKDIR /workspace/router
RUN git checkout e1b019ccb84ba2a5c60d36adae2440ac9f5bc34f

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build all packages (needed for TypeScript declarations)
ENV CI=1
ENV NX_DAEMON=false
RUN pnpm build:all

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
