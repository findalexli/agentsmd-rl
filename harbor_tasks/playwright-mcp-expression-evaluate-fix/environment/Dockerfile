FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install python3 for test runner, git, and build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (filter=blob:none for faster clone of large monorepo)
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout cec7b21afa00c0f48e46859c683680a2c6e9e029 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install dependencies (needed for tsc and tests)
RUN npm ci --silent 2>&1 || npm install --silent 2>&1 || true

# Build the project (needed for running MCP tests)
RUN npm run build 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
