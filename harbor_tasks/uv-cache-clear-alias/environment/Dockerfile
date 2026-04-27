FROM rust:1.93-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_TERM_COLOR=never
ENV CARGO_INCREMENTAL=0
ENV RUST_BACKTRACE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git uv \
 && cd uv \
 && git checkout 5d52a358301d9065923647a00de6a135a508ba1e

WORKDIR /workspace/uv

# Pre-build the `uv` binary in debug mode. Limit parallel link jobs to avoid
# OOM on memory-constrained hosts. This populates ~/.cargo/registry and
# /workspace/uv/target so that solve.sh's incremental rebuild is fast.
RUN cargo build --bin uv -j 4 2>&1 | tail -20

RUN mkdir -p /logs/verifier
