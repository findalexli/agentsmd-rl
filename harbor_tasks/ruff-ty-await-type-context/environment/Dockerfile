FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

ARG BASE_COMMIT=f283ddc382bf2d2825d21d4a59f2610ed97e5302
RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo builds are fast
RUN cargo fetch

# Pre-compile deps (warm incremental cache for the ty_python_semantic crate)
RUN cargo check -p ty_python_semantic 2>&1 || true

ENV PYTHONDONTWRITEBYTECODE=1
