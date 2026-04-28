FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain pinned to the version used by the repo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain 1.94
ENV PATH="/root/.cargo/bin:${PATH}"

RUN rustup component add clippy rustfmt

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 62a863cf518086135dfd2321c92fbc3823f95de8 && \
    git checkout FETCH_HEAD

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/ruff

# Pre-compile ty_project crate (check mode) to warm compilation cache.
# Incremental rebuilds after a single-file change will be much faster.
ENV CARGO_PROFILE_DEV_OPT_LEVEL=1
RUN cargo check -p ty_project 2>&1
