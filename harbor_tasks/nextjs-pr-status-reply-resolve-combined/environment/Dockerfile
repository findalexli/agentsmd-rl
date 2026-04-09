FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for large monorepo)
RUN git clone --depth=1 https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git fetch --depth=1 origin fea754747872122d167dd8bf1fc5581044e50521 && \
    git checkout fea754747872122d167dd8bf1fc5581044e50521 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
