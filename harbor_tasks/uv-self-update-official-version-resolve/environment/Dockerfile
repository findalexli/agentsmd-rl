FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config \
    libssl-dev python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the base commit (before the fix)
RUN git clone https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout 10477cd1ce808690a024e867417ce58df901d0c1

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.email "test@test.com" && git config user.name "Test"

# Install required Rust toolchain from rust-toolchain.toml
RUN rustup toolchain install 1.94.0 && rustup default 1.94.0

# Pre-fetch cargo dependencies
RUN cargo fetch

# Pre-build test binaries so test-time compilation is incremental
RUN cargo test -p uv-bin-install --no-run 2>&1 || true
RUN cargo test -p uv --lib --no-run 2>&1 || true