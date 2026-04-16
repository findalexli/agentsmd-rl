# TanStack Router benchmark task environment
FROM node:22-slim

# Install python3 for pytest runner + git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone TanStack router at base commit (parent of merge commit)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout 7640f6e3f5d946ca1fd32729050d12642cf38502

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build packages (needed for tests to run)
RUN pnpm build:all

# Create log directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
