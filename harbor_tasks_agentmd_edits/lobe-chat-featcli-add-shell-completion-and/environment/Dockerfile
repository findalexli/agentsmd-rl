FROM oven/bun:1.2-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/lobehub/lobe-chat.git /workspace/lobe-chat && \
    cd /workspace/lobe-chat && \
    git checkout 12280badbdf288b7018a9d5b907898780cd31a96 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lobe-chat/apps/cli

# Install dependencies (needed for the tests to run)
RUN bun install --frozen-lockfile || bun install

WORKDIR /workspace/lobe-chat

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
