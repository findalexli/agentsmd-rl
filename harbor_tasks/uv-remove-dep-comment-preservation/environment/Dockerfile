FROM rust:1.86-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux pkg-config python3 libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 46c9bac182d64359cef45d51fd796b81b3736f8b && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.name "test" && git config user.email "test@test.com"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch 2>/dev/null || true

# Pre-build workspace test deps (much faster than full uv binary)
RUN cargo test -p uv-workspace --lib --no-run 2>/dev/null || true