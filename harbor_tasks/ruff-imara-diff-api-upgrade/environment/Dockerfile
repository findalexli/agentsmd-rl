FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git ruff && \
    cd ruff && \
    git checkout 459f20220ac0f8467e47779f21420fecab154c9d && \
    git checkout -b task-branch

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo check is fast
RUN cargo fetch

# Pre-compile all deps (warm incremental cache)
# This makes test-time cargo check only need to recompile changed crates
RUN cargo check -p ruff_dev 2>&1 || true

# Copy test/scoring infrastructure

ENV PYTHONDONTWRITEBYTECODE=1