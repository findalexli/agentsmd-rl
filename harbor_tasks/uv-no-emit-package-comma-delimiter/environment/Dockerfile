FROM rust:1.86-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux pkg-config python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the base commit (before the fix)
RUN git clone https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout 5e25583c42b01fe8b1fae3b8ef05057cfdb4090c

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.name "test" && git config user.email "test@test.com"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch 2>/dev/null || true