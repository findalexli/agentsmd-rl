FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# workerd is a large monorepo — shallow clone at base commit
RUN git init /workspace/workerd && \
    cd /workspace/workerd && \
    git remote add origin https://github.com/cloudflare/workerd.git && \
    git fetch --depth=1 origin bca5351754a7d3ee0568971d57435859bc3a71e6 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
