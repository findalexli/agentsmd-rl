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
    git checkout 5f7e0346bc946d7fb484b285d49d351d3a54d526 && \
    git checkout -b task-branch

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo builds are fast
RUN cargo fetch

# Pre-compile deps (warm incremental cache for the ruff_linter crate)
RUN cargo check -p ruff_linter 2>&1 || true

# Copy test/scoring infrastructure

ENV PYTHONDONTWRITEBYTECODE=1