FROM rust:1.95-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_INCREMENTAL=0
ENV RUSTFLAGS="-C debuginfo=0 -C codegen-units=256"

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        pkg-config \
        libssl-dev \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install pinned pytest in a venv (Debian python externally-managed)
RUN python3 -m venv /opt/pyvenv \
    && /opt/pyvenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/pyvenv/bin:${PATH}"

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git
WORKDIR /workspace/ruff
RUN git checkout 65d768e4e2a7133b7bcddc4de3027259b4578d8a

# Pre-build the ty binary in debug mode (debug is faster to compile and the AGENTS.md
# guidance prefers debug for development). This caches the compile so subsequent
# rebuilds (after the agent edits Rust source) are incremental and quick.
RUN cargo build --bin ty

RUN mkdir -p /logs/verifier
