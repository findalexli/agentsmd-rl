FROM rust:1.85-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update --allow-insecure-repositories || true \
    && apt-get install -y --allow-unauthenticated \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    pkg-config libssl-dev cmake \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow for speed)
RUN git init /workspace/uv && \
    cd /workspace/uv && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 8b0e9e5fb997cbdc2f4f58b43cd805d22e57bd1b && \
    git checkout FETCH_HEAD

WORKDIR /workspace/uv

RUN git config user.email "agent@test" && git config user.name "Agent"

# Pre-fetch cargo dependencies to speed up incremental builds
RUN cargo fetch 2>/dev/null || true

# Pre-build uv-resolver crate (so agent changes only need incremental recompile)
RUN cargo check -p uv-resolver 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
