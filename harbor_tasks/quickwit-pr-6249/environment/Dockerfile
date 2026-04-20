FROM rust:1.85-slim

ENV CARGO_INCREMENTAL=0 \
    RUST_BACKTRACE=1 \
    QW_DISABLE_TELEMETRY=1

WORKDIR /workspace

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libssl-dev \
    git \
    python3 \
    python3-pip \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
# Use reference clone for faster cloning, then checkout specific commit
RUN git clone --filter=blob:none --no-checkout https://github.com/quickwit-oss/quickwit.git quickwit-repo && \
    cd quickwit-repo && \
    git fetch --depth=1 origin 8565b8a349662c3648648296501958ccec15ab61 && \
    git checkout 8565b8a349662c3648648296501958ccec15ab61

WORKDIR /workspace/quickwit-repo/quickwit

# Build only the quickwit-cluster crate to verify compilation works
RUN cargo build -p quickwit-cluster --features=testsuite 2>&1 | tail -20

# Pre-run cargo to cache dependencies
RUN cargo test -p quickwit-cluster --features=testsuite --no-run 2>&1 | tail -5

WORKDIR /workspace
