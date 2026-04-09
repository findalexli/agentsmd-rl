FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (large monorepo — use blob filter)
RUN git clone --filter=blob:none https://github.com/denoland/deno.git /workspace/deno && \
    cd /workspace/deno && \
    git checkout 8295a2cf2aabe2ecd9ccce8a802d0d5d61095a2e && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
