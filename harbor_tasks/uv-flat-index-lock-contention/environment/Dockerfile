FROM rust:1.86-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config \
    python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the buggy base commit (before the fix)
RUN git clone https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout 9d45e7f8177e6f60e084ba52b2a32a56edf237c7

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential commits
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies to speed up test builds
RUN cargo fetch

# Pre-compile dependencies (not the crate itself) so cargo check is fast during tests
RUN cargo check -p uv-client 2>&1 || true