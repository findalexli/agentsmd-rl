FROM rust:bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=627e2a04269400ea88f65e64797666ad32604204

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Pre-build to cache all dependencies (incremental builds will be fast)
RUN cargo build --bin ruff

# Configure git for patches
RUN git config user.email "test@test.com" && git config user.name "Test"