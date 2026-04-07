FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large monorepo)
RUN git clone --depth=1 https://github.com/prisma/prisma.git /workspace/prisma && \
    cd /workspace/prisma && \
    git fetch --depth=1 origin 3fd1431decb1013969c9ef061f8c391e715fe973 && \
    git checkout 3fd1431decb1013969c9ef061f8c391e715fe973 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prisma

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
