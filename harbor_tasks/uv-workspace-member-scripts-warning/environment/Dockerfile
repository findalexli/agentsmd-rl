FROM rust:1.93-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=never \
    RUST_BACKTRACE=1 \
    UV_NO_TELEMETRY=1

# System deps: build tools, git, curl, Python (uv needs an interpreter at runtime),
# and python3-venv for sync to create venvs in test fixtures.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        curl \
        pkg-config \
        libssl-dev \
        build-essential \
        python3 \
        python3-venv \
        python3-pip \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Pin pytest so test.sh installs deterministically
RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

# Clone uv at the base commit (parent of merge commit for PR #18389)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git uv \
    && cd uv \
    && git checkout 5dc986d367b881e3e8f2a7b2560f78b6b1cbb1c1

WORKDIR /workspace/uv

# Pre-build the `uv` binary (debug, no release) to populate Cargo's target/ cache
# so that the agent's incremental rebuild after a small patch is fast.
# Tests will recompile only the `uv` crate after the agent's edit.
RUN cargo build -p uv --bin uv 2>&1 | tail -50

# Make sure the prebuilt binary exists where tests will look for it
RUN test -x /workspace/uv/target/debug/uv

# Logs directory for harness reward
RUN mkdir -p /logs/verifier
