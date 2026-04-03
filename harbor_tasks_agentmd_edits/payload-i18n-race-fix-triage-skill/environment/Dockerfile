FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit (large monorepo)
RUN mkdir -p /workspace/payload && \
    cd /workspace/payload && \
    git init && \
    git remote add origin https://github.com/payloadcms/payload.git && \
    git fetch --depth=1 origin d3b12a1b06eff5831dca3bbb15f2ad064e663102 && \
    git checkout d3b12a1b06eff5831dca3bbb15f2ad064e663102 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/payload

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
