FROM rust:1.94-slim

ENV CARGO_TERM_COLOR=never \
    RUST_BACKTRACE=0 \
    DEBIAN_FRONTEND=noninteractive

# System deps: git for cloning, python3 (universal test harness),
# build-essential for any C deps that crates pull in, ca-certificates + pkg-config for TLS/git over https.
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    pkg-config \
    libssl-dev \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Pinned pytest for the test harness.
RUN pip3 install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-report==1.5.0

# Clone ruff at the PR's base commit.
ARG REPO_URL=https://github.com/astral-sh/ruff.git
ARG BASE_COMMIT=61f9a0a5763fb068cd2f26c0ee9d63a277fb26c2
WORKDIR /workspace
RUN git clone --filter=blob:none ${REPO_URL} ruff && \
    cd ruff && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ruff

# Pre-build the `ty` binary to warm the cargo cache so test runs and gold rebuild are fast.
# Use debug build (project policy in AGENTS.md: debug builds preferred for development).
RUN cargo build --bin ty 2>&1 | tail -20

RUN mkdir -p /logs/verifier
