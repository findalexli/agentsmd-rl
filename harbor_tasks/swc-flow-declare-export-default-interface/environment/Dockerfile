FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        pkg-config \
        libssl-dev \
        build-essential \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-report==1.5.0

RUN rustup component add rustfmt clippy

ENV CARGO_TERM_COLOR=never
ENV CARGO_NET_RETRY=5
ENV CARGO_HOME=/usr/local/cargo
ENV RUSTC_WRAPPER=

WORKDIR /workspace

RUN git init /workspace/swc && \
    cd /workspace/swc && \
    git remote add origin https://github.com/swc-project/swc.git && \
    git fetch --depth=1 origin 99e61c4cc172b772437dcabcf8f937a8f24dc4bd && \
    git checkout FETCH_HEAD

WORKDIR /workspace/swc

# Pre-fetch dependencies and pre-build the parser crate (with flow feature) so
# subsequent test runs only need to recompile the touched parser file plus the
# small regression test we add at run time.
RUN cargo fetch
RUN cargo build -p swc_ecma_parser --features flow --tests

RUN mkdir -p /logs/verifier
