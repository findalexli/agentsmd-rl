FROM rust:1.85-slim

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
    git fetch --depth=1 origin b491f7ebed9ea3be8ff7990dd6119c77c57baa74 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo builds are fast
RUN cargo fetch

# Pre-compile deps (warm incremental cache for the ruff_linter crate)
RUN cargo check -p ruff_linter 2>&1 || true

# Pre-build the ruff binary so agent changes only need incremental rebuild
RUN cargo build --bin ruff 2>&1 || true

# Copy test/scoring infrastructure

ENV PYTHONDONTWRITEBYTECODE=1