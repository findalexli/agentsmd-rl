FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install python3 for test runner, git for cloning, and basic build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow clone for faster builds)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout 3af4cc14ea400ebc01fdc267f3d3495bfe086a7e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Pre-fetch some dependencies for faster agent builds (optional, helps with pnpm install later)
# Note: We don't run full install here to keep image size reasonable
# The test code itself doesn't need the full Next.js build

# Install TypeScript globally for syntax checking
RUN npm install -g typescript

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
