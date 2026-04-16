FROM node:22-slim

# Install Python for test runner, git for cloning, and pytest via apt
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pytest \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/withastro/astro.git \
    && cd astro \
    && git checkout 6d182fe267586e2ee57113ad559912a456019306

WORKDIR /workspace/astro

# Install pnpm
RUN npm install -g pnpm

# Install dependencies (CI mode for non-interactive)
ENV CI=true
# We need to install at root level to get workspace dependencies set up
RUN pnpm install --frozen-lockfile 2>&1 || pnpm install 2>&1

# Build the workspace packages that astro depends on
# We need @astrojs/internal-helpers, @astrojs/markdown-remark, etc. for TypeScript compilation
RUN pnpm run build:ci 2>&1 || echo "Build completed with some errors"

# Create logs directory
RUN mkdir -p /logs/verifier

# Verify the target file exists and has the expected content
RUN test -f packages/astro/src/vite-plugin-css/index.ts \
    && grep -q "ensureModulesLoaded" packages/astro/src/vite-plugin-css/index.ts

# Default working directory for tests
WORKDIR /workspace/astro
