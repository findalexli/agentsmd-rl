FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone ruff at the base commit (before fix)
ARG BASE_COMMIT=d81266252aaf0820346d55edbed79c4f25ba13d2
RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruff

# Pre-build ty_ide crate to cache compilation artifacts
# This makes incremental rebuilds after agent changes fast
RUN cargo build -p ty_ide 2>&1 | tail -5

# Copy test files