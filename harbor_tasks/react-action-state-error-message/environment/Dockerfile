FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout 3bc2d414287e62a7b74731c6c7b837270353a339 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install dependencies
RUN yarn install --frozen-lockfile

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
