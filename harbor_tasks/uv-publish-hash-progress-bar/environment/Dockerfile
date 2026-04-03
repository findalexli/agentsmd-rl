FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config python3 tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 7c2f6c696bdeb6b04166982b33b8fdca87578391 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Pre-fetch dependencies to speed up builds
RUN cargo fetch

# Pre-compile to enable incremental builds in test.sh (within 120s timeout)
RUN cargo check -p uv-publish -p uv 2>&1 || true
RUN cargo test -p uv-publish --no-run 2>&1 || true

# Configure git user for agent
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

ENV PYTHONPATH=/repo