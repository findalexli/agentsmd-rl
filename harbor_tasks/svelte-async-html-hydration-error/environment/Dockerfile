FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Enable corepack for pnpm version management
RUN corepack enable

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sveltejs/svelte.git /workspace/svelte && \
    cd /workspace/svelte && \
    git checkout 54ba176d2c9068f2e6df9249764bb7766ec1b69d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/svelte

# Install dependencies (compiler source is ESM, importable after install)
RUN pnpm install --frozen-lockfile

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
