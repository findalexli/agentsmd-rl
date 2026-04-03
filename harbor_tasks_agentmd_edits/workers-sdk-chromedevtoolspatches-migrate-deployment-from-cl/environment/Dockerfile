FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Shallow clone at base commit
RUN git init /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git remote add origin https://github.com/cloudflare/workers-sdk.git && \
    git fetch --depth=1 origin 3b81fc6a75857d5c158824f17d9316adc55878fc && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
