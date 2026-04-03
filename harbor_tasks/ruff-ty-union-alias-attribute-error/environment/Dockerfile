FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone repo at base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 6e76b4cd8a27c2b22263204b83372c4f3720bf79 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Fetch dependencies (cached in Docker layer)
RUN cargo fetch

# Pre-compile ty binary to cache dependency compilation
# Agent's changes only need incremental recompilation of the changed crate
RUN cargo build --bin ty 2>&1 || true

WORKDIR /repo