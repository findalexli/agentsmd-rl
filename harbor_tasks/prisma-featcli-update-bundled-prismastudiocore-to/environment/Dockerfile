FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (blob-filter for large monorepo)
RUN git clone --filter=blob:none https://github.com/prisma/prisma.git /workspace/prisma && \
    cd /workspace/prisma && \
    git checkout 32fb24b53c2a46971f3093eee9934c18e0f47642 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prisma

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
