FROM rust:1.95-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_TERM_COLOR=never
ENV RUST_BACKTRACE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        pkg-config \
        libssl-dev \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv && \
    /opt/pyenv/bin/pip install --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1
ENV PATH="/opt/pyenv/bin:${PATH}"

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git uv && \
    cd uv && \
    git checkout 46c9bac182d64359cef45d51fd796b81b3736f8b

WORKDIR /workspace/uv

RUN cargo fetch

RUN cargo test -p uv-workspace --tests --no-run --locked 2>&1 | tail -20

RUN mkdir -p /logs/verifier
