FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/next.js && \
    cd /workspace/next.js && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin 56d75a0b77f2ceda8ea747810275da8e0a9a3d71 && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Install pnpm (Next.js uses pnpm)
RUN npm install -g pnpm

# Pre-install dependencies for faster test execution (but don't build)
RUN pnpm install --frozen-lockfile || true

# Build just the render-result and send-payload modules for testing
RUN pnpm --filter=next exec taskr ncc render-result || true
RUN pnpm --filter=next exec taskr ncc send-payload || true

# Verifier output directory
RUN mkdir -p /logs/verifier
