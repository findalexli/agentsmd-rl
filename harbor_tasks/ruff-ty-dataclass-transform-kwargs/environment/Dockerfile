FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone ruff at base commit (before the fix)
RUN git clone --no-checkout https://github.com/astral-sh/ruff.git /repo \
    && cd /repo \
    && git checkout 32f644c3bfa09271cc54ca04f7259fbf8a99b81f

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.name "agent" && git config user.email "agent@test.com"

# Pre-build ty binary to speed up test runs
RUN cargo build --bin ty 2>&1 | tail -5

ENV PATH="/repo/target/debug:${PATH}"