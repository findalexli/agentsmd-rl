FROM rust:1.94-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone ruff at the base commit (before fix)
ARG BASE_COMMIT=c37535dd792bf8a46fb0be1b6a70a6483d0c6833
RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo builds are fast
RUN cargo fetch

# Pre-compile deps (warm incremental cache for ty_python_semantic crate)
RUN cargo check -p ty_python_semantic 2>&1 || true

ENV PYTHONDONTWRITEBYTECODE=1
