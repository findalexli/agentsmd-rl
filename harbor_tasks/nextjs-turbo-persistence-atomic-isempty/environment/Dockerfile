FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (blob-less for large monorepo)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js && \
    cd /workspace/next.js && \
    git checkout e513488d0d3bc19ae9b16b08ef43add7e4faab7c && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/next.js

# No Rust toolchain needed — tests use Python source analysis
# (cargo check would exceed timeout on this monorepo)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
