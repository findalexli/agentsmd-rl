FROM rust:1.86-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux pkg-config python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 17afca33e9d7d678a1e00df280247eed39d8231d && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.name "test" && git config user.email "test@test.com"

# Pre-fetch and pre-compile dependencies to speed up test runs.
# This compiles the test binary so only source changes trigger recompilation.
RUN cargo fetch 2>/dev/null || true
RUN cargo test -p uv-distribution-types --no-run 2>/dev/null || true
