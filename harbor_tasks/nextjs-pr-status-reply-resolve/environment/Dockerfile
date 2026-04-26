FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (next.js is a large monorepo — blob:none keeps it lean)
RUN git init /workspace/nextjs && \
    cd /workspace/nextjs && \
    git remote add origin https://github.com/vercel/next.js.git && \
    git fetch --depth=1 origin fea754747872122d167dd8bf1fc5581044e50521 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/nextjs

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
