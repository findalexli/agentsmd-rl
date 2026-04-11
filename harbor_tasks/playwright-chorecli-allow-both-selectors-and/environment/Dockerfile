FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/microsoft/playwright.git /workspace/playwright && \
    cd /workspace/playwright && \
    git checkout 35f853d5c293c901ea66a9aa3f56f6879a94e66a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/playwright

# Install project deps (needed for esbuild to bundle test helpers)
RUN npm install 2>&1 | tail -5 || true

# Pre-bundle locator parser for behavioral tests (pure isomorphic module, no browser deps)
RUN npx esbuild packages/playwright-core/src/utils/isomorphic/locatorParser.ts \
        --bundle --outfile=/tmp/locatorParser.cjs --format=cjs --platform=node 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
