FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (required — this is a Rust project)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal
ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/ruff && \
    cd /workspace/ruff && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 37f5d61595f88591b91b914aa05550644300ce19 && \
    git checkout FETCH_HEAD

# Pre-build ruff binary + test harness to cache compiled dependencies.
# After the agent's 1-2 file change, incremental rebuild takes ~30-60s.
RUN cd /workspace/ruff && cargo build --bin ruff 2>&1 | tail -5
RUN cd /workspace/ruff && cargo test --package ruff_linter --no-run 2>&1 | tail -5

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/ruff
