FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config \
    python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the buggy base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin b38bea427cca74f993c78213522a16a902b6046e && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential commits
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies to speed up test builds
RUN cargo fetch