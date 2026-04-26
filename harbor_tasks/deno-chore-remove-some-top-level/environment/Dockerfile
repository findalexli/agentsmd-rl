FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/deno && \
    cd /workspace/deno && \
    git remote add origin https://github.com/denoland/deno.git && \
    git fetch --depth=1 origin 0b38d25ba7c1893757e15fbb2a68537b0191321f && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Pre-fetch cargo dependencies for faster builds
RUN cargo fetch 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
