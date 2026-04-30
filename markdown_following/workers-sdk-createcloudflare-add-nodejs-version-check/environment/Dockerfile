FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (sparse — monorepo is large)
RUN git init /workspace/workers-sdk && \
    cd /workspace/workers-sdk && \
    git remote add origin https://github.com/cloudflare/workers-sdk.git && \
    git fetch --depth=1 origin 0de69890c8503bb67e391e7ad5578c7001b7798e && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workers-sdk

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
