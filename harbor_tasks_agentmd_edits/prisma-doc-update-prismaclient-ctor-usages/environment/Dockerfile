FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large monorepo)
RUN git init /workspace/prisma && \
    cd /workspace/prisma && \
    git remote add origin https://github.com/prisma/prisma.git && \
    git fetch --depth=1 origin 76bb95b96b663cfbd622a7d1d62f78619f2cff2c && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prisma

# No project deps needed — tests only read file content
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
