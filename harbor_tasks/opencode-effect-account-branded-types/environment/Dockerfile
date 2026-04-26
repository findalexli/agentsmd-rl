FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun (needed for workspace dependency installation)
RUN npm install -g bun@latest

# Clone repo at base commit
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 2aae0d3493ac51aa2fd3929c6db0814ab795b04b && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Install workspace dependencies (needed for Effect imports in test execution)
RUN bun install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
