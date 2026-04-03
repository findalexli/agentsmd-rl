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
RUN git clone --filter=blob:none https://github.com/wei/socialify.git /workspace/socialify && \
    cd /workspace/socialify && \
    git checkout a4782705076144332a7ca53d4d35afdcd0ddb93e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/socialify

# Install deps (agent needs these to build/verify; pnpm install needed after version bump)
RUN pnpm install --frozen-lockfile

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
