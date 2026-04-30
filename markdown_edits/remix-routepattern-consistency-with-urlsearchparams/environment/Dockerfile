FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Shallow clone at base commit (remix is a large monorepo)
RUN git init /workspace/remix && \
    cd /workspace/remix && \
    git remote add origin https://github.com/remix-run/remix.git && \
    git fetch --depth=1 origin 92a9b9df4ef4c7096973a6d1df040f512e7ccee2 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/remix

# Install dependencies
RUN pnpm install

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
