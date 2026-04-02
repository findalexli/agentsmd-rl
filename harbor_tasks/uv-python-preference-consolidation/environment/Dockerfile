FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the base commit (before the fix)
RUN git clone https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout bd2e0c9b09551c6570b14c4da80364fe90805b78 \
    && git config user.name "test" \
    && git config user.email "test@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Pre-fetch and pre-compile dependencies to speed up cargo check at test time
RUN cargo fetch
RUN cargo check -p uv-python -p uv 2>&1 || true
RUN cargo test -p uv-python --lib --no-run 2>&1 || true