FROM rust:1.94-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin a84a58fef88968e36c0b070f0ab9a4bff7a05389 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo builds are fast
RUN cargo fetch

# Pre-compile deps (warm incremental cache for the ruff_server crate)
RUN cargo check -p ruff_server 2>&1 || true

# Copy test/scoring infrastructure

ENV PYTHONDONTWRITEBYTECODE=1