FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (treeless clone for large monorepo)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout def0e3aabfa112ada22ece9297501c52471d34bd && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
