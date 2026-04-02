FROM rust:1.94-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone repo at base commit (before the fix)
RUN git clone --no-checkout https://github.com/astral-sh/ruff.git /repo \
    && cd /repo \
    && git checkout c4c6c22d7b73342b3dfebcd526c466fa1df759c8

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Fetch dependencies (cached in Docker layer)
RUN cargo fetch

# Pre-compile ty binary to cache dependency compilation
# Agent's changes only need incremental recompilation of the changed crate
RUN cargo build --bin ty 2>&1 || true

WORKDIR /repo