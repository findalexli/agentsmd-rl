FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Backstage is a large monorepo — use shallow clone
RUN git init /workspace/backstage && \
    cd /workspace/backstage && \
    git remote add origin https://github.com/backstage/backstage.git && \
    git fetch --depth=1 origin 1ee5b28e41c274ea38c16a07290387763b5e2284 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/backstage

# Install dependencies
RUN yarn install --immutable

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
