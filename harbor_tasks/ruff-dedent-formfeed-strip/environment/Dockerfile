FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff && \
    cd /workspace/ruff && \
    git checkout 1f430e68af6e627569776dfbcd03b98ac7c29eb6 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/ruff

# Pre-fetch deps and warm incremental build cache
RUN cargo fetch
RUN cargo build --bin ruff 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
