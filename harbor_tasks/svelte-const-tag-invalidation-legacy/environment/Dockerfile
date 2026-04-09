FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip python3-venv tmux && \
    rm -rf /var/lib/apt/lists/*

RUN corepack enable && corepack prepare pnpm@10.4.0 --activate

RUN git clone --filter=blob:none https://github.com/sveltejs/svelte.git /workspace/svelte && \
    cd /workspace/svelte && \
    git checkout ff3495dc05bbdd81a225ba43446d82171b4413e3 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/svelte

# Install all monorepo deps (includes vitest, jsdom for tests)
RUN pnpm install --frozen-lockfile

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
