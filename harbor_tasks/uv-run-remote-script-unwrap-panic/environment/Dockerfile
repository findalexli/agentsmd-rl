FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update --allow-insecure-repositories || true \
    && apt-get install -y --allow-unauthenticated \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    pkg-config libssl-dev cmake \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone --no-checkout https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout 867e535f2a5f7f2b1f22a0ccc52fc6da5b01ac3c

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch 2>/dev/null || true