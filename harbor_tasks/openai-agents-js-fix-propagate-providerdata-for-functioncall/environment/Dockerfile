FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Enable corepack for pnpm
RUN corepack enable

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git /workspace/openai-agents-js && \
    cd /workspace/openai-agents-js && \
    git checkout 85b6c896ea19d8f859ba86f3993054a832a93c64 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/openai-agents-js

# Install deps and build (dist/ needed for tsx/vitest to resolve workspace packages)
RUN pnpm install --frozen-lockfile && pnpm build

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
