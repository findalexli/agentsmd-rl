FROM rust:1.94.0-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=never \
    CARGO_INCREMENTAL=0 \
    RUSTFLAGS="-C debuginfo=0" \
    CARGO_PROFILE_TEST_DEBUG=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        pkg-config \
        libssl-dev \
        build-essential \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace

ARG REPO_URL=https://github.com/astral-sh/uv.git
ARG BASE_COMMIT=17afca33e9d7d678a1e00df280247eed39d8231d

RUN git clone --filter=blob:none "$REPO_URL" uv \
 && cd uv \
 && git checkout "$BASE_COMMIT" \
 && git config user.email "task@example.com" \
 && git config user.name  "task"

WORKDIR /workspace/uv

# Pre-warm cargo cache by building uv-distribution-types tests once.
# This downloads & compiles all transitive deps so later `cargo test`
# during NOP / GOLD validation is fast.
RUN cargo build --package uv-distribution-types --tests --quiet 2>&1 | tail -40

WORKDIR /workspace
