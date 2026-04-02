FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@example.com" \
    && git config --global user.name "Agent"

# Clone ruff at base commit (parent of the merge commit for PR #24151)
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /repo \
    && cd /repo && git checkout 6cff03427e386e38dc2ead0cc7718a71bfa288f8

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Pre-build ty binary to cache compilation artifacts
RUN CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo build --bin ty 2>&1 | tail -5

# Copy test infrastructure

ENV PYTHONPATH=/repo