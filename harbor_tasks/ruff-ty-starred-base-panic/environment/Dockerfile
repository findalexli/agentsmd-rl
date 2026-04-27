FROM rust:1.95-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    curl \
    pkg-config \
    libssl-dev \
    build-essential \
    cmake \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4

RUN mkdir -p /logs/verifier

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff && \
    cd /workspace/ruff && \
    git checkout 65d768e4e2a7133b7bcddc4de3027259b4578d8a

WORKDIR /workspace/ruff

# Pre-build the ty binary at the base commit so the Docker image has a warm
# cargo cache. Drop incremental compilation artifacts and registry sources
# (kept at .crate level only) in the same layer to keep the image smaller —
# the gold/agent fix rebuilds only the touched crates on top of cached deps.
RUN cargo build --bin ty 2>&1 | tail -5 \
    && /workspace/ruff/target/debug/ty --help > /dev/null \
    && rm -rf /workspace/ruff/target/debug/incremental \
    && rm -rf /usr/local/cargo/registry/src
