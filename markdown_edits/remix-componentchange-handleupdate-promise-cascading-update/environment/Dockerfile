FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

RUN corepack enable

# Shallow clone at base commit
RUN mkdir -p /workspace/remix && \
    cd /workspace/remix && \
    git init && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin 649aecadeb54fc3027a2b6a85020dd31421b5327 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install dependencies (needed to run component package tests)
RUN pnpm install --frozen-lockfile 2>/dev/null || pnpm install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
