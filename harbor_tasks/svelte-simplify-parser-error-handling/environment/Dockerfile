FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

RUN corepack enable

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/sveltejs/svelte.git /workspace/svelte && \
    cd /workspace/svelte && \
    git checkout 8966601dcd14582cd46d4fbb7c5cf1b444292255 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/svelte

# Install dependencies (needed for acorn syntax checks and agent testing)
RUN pnpm install --frozen-lockfile

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
