FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin ca3343e4cf25e8314c26cce2031abb67ed6a3b16 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ruff

# Pre-fetch deps and warm incremental compile cache
RUN cargo fetch
RUN cargo build --bin ty 2>&1 | tail -5

ENV PYTHONDONTWRITEBYTECODE=1