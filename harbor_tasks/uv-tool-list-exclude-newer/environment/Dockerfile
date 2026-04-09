FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update --allow-insecure-repositories || true \
    && apt-get install -y --allow-unauthenticated \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    pkg-config libssl-dev cmake \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /workspace/uv && \
    cd /workspace/uv && \
    git checkout 2cf99b91ec336f3884c400634e61ec6d1bd77e5a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/uv

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch 2>/dev/null || true

RUN mkdir -p /logs/verifier
