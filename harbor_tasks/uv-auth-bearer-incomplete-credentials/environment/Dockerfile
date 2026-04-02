FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the base commit (before the fix)
RUN git clone https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout e169f431729c6dcf2cf3e518c0c86e0f962538f1 \
    && git config user.name "test" \
    && git config user.email "test@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /repo