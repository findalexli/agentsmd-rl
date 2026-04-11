FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (LTS) which includes corepack
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    corepack enable

# Shallow clone at base commit (large monorepo — only need file contents)
RUN git init /workspace/remix && \
    cd /workspace/remix && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin b29fc874293468babb25b90e95edc208f1d652be && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install dependencies
RUN pnpm install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
