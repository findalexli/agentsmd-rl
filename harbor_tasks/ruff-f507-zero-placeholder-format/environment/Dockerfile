FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git ruff && \
    cd ruff && \
    git checkout 690ef81f553ca0ce2f477e8030f4ab49abea4b01 && \
    git checkout -b task-branch

WORKDIR /workspace/ruff

# Pre-fetch all dependencies so cargo builds are fast
RUN cargo fetch

# Pre-build the ruff binary so test runs only need incremental recompilation
RUN cargo build --bin ruff

# Copy test/scoring infrastructure

ENV PYTHONDONTWRITEBYTECODE=1