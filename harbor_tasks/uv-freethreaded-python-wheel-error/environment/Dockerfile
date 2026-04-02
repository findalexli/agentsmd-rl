FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone --no-checkout https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout 87da0ce43ac12fc50e28931f42b1164453f04790

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies and warm the build cache
RUN cargo fetch 2>/dev/null || true
RUN cargo check -p uv-distribution 2>/dev/null || true
RUN cargo check -p uv-platform-tags 2>/dev/null || true