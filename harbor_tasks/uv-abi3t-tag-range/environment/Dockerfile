FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /workspace/uv && \
    cd /workspace/uv && \
    git checkout b7d5faf568b30c86daf7503f8518e11cbfeeaa81 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Pre-fetch deps and build the platform-tags crate for faster agent builds
RUN cargo fetch && cargo check --package uv-platform-tags 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
