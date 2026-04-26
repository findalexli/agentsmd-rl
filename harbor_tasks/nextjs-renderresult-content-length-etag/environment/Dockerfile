FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install python3 for pytest test runner, git for cloning, curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone Next.js repo at base commit (pre-fix)
# Using --filter=blob:none for faster clone of this large monorepo
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin fb85660ab1f70e294465af0074dc7c941e3540ca && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Install pnpm (Next.js uses pnpm)
RUN npm install -g pnpm

# Pre-install dependencies for faster test execution
# We only install what's needed for the specific package we're testing
RUN pnpm install --frozen-lockfile --filter=next --filter=@next/test-utils 2>&1 || \
    pnpm install --filter=next --filter=@next/test-utils 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
