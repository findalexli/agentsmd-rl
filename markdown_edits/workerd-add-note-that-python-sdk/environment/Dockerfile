FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# workerd is a large monorepo — use git init + shallow fetch
RUN mkdir -p /workspace/workerd && \
    cd /workspace/workerd && \
    git init && \
    git remote add origin https://github.com/cloudflare/workerd.git && \
    git fetch --depth=1 origin c91cf4910046c3f4eeffa713cc15a5129ac2ad19 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# No pip deps needed — tests only use stdlib (hashlib, pathlib, ast, subprocess)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
