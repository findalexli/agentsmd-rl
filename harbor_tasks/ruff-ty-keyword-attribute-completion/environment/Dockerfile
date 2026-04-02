FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone ruff at the base commit (before fix)
ARG BASE_COMMIT=4aabc71fa2594b5c90105cc963cb04c1c4d52f51
RUN git clone --no-checkout https://github.com/astral-sh/ruff.git /workspace/ruff \
    && cd /workspace/ruff \
    && git checkout ${BASE_COMMIT}

RUN mkdir -p /logs/verifier

WORKDIR /workspace/ruff

# Install cargo-nextest (used by test.sh)
RUN curl -LsSf https://get.nexte.st/latest/linux | tar zxf - -C /usr/local/cargo/bin

# Pre-build ty_ide crate to cache compilation artifacts
# This makes incremental rebuilds after agent changes fast
RUN cargo build -p ty_ide 2>&1 | tail -5