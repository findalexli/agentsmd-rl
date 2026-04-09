FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# React uses yarn 1.22.22 via corepack
RUN corepack enable

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout e0cc7202e14418b453c69c4f06dc00c64151f202 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install dependencies (needed for jest tests in verifier)
RUN yarn install --frozen-lockfile --network-timeout 600000

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
