FROM rust:1.91-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_TERM_COLOR=never
ENV RUST_BACKTRACE=1
# Drop debug info from dev/test profiles — the lancedb test binary is huge
# and the link step OOMs the linker on small VMs otherwise.
ENV CARGO_PROFILE_DEV_DEBUG=0
ENV CARGO_PROFILE_TEST_DEBUG=0
ENV CARGO_INCREMENTAL=0
ENV CARGO_BUILD_JOBS=2

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    pkg-config \
    libssl-dev \
    protobuf-compiler \
    libprotobuf-dev \
    cmake \
    build-essential \
    clang \
    python3 \
    python3-pip \
    python3-venv \
    curl \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/lancedb/lancedb.git \
 && cd lancedb \
 && git checkout d5948576b92744c39302f6e9130da0456792fe56

WORKDIR /workspace/lancedb

RUN git config user.email "harbor@example.com" \
 && git config user.name  "harbor"

RUN cargo fetch

RUN cargo build --tests -p lancedb

RUN mkdir -p /logs/verifier
