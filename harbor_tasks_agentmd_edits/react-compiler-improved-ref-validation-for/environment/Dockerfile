FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# React is a large monorepo — use shallow clone with sparse checkout for compiler/
RUN git clone --filter=blob:none https://github.com/facebook/react.git /workspace/react && \
    cd /workspace/react && \
    git checkout c0060cf2a695d719152c939cfc3cced8f7da3e52 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/react

# Install yarn and compiler dependencies needed for fixture tests
RUN corepack enable && \
    cd compiler && \
    yarn install --frozen-lockfile 2>&1 || yarn install 2>&1

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
