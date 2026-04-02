FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone ruff at the base commit (before fix)
ARG BASE_COMMIT=3465d7f1a2ed13c03aeca5f9b2d764b00ab0ab32
RUN git clone --no-checkout https://github.com/astral-sh/ruff.git /workspace/ruff \
    && cd /workspace/ruff \
    && git checkout ${BASE_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruff

# Pre-build ty binary to cache compilation artifacts
# This makes incremental rebuilds after agent changes fast (~60-120s)
RUN cargo build --bin ty 2>&1 | tail -5

# Tests and rubric are mounted at runtime