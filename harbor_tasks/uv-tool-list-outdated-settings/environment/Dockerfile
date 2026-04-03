FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config \
    libssl-dev python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin c1cd212dd5a927d9e354c44d89a307f6a6f4df37 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git user for potential commits
RUN git config user.email "bench@test.local" \
    && git config user.name "Benchmark"

# Fetch all cargo dependencies
RUN cargo fetch

# Pre-build dependencies (not the workspace crates themselves) to speed up incremental builds.
RUN cargo check -p uv 2>&1 || true

ENV CARGO_INCREMENTAL=1
