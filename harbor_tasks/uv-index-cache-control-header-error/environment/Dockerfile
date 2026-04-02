FROM rust:1.94-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /logs/verifier

WORKDIR /src
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git . \
    && git checkout 1b6b7befb1b7160ff32c8692bbf24ef98aae3fa7

# Pre-fetch all dependencies and pre-build the test target crates to cache compilation
RUN cargo fetch
RUN cargo check -p uv-distribution-types -p uv-client 2>&1 || true
RUN cargo test -p uv-distribution-types --no-run 2>&1 || true

# Configure git
RUN git config user.name "test" && git config user.email "test@test.com"

WORKDIR /src