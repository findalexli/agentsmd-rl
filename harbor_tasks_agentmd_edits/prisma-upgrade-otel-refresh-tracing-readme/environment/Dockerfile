FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo, use filter)
RUN git clone --filter=blob:none https://github.com/prisma/prisma.git /workspace/prisma && \
    cd /workspace/prisma && \
    git checkout 423b58507879080bdc1273ca5d30b3de87e5b766 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prisma

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
