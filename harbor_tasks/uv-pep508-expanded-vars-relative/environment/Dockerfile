FROM rust:1.94-slim

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=never \
    CARGO_NET_RETRY=3 \
    RUST_BACKTRACE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        build-essential \
        pkg-config \
        libssl-dev \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/pyenv \
    && /opt/pyenv/bin/pip install --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.3.7
ENV PATH=/opt/pyenv/bin:$PATH

WORKDIR /workspace

RUN git init /workspace/uv && \
    cd /workspace/uv && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin b0ad910b0289b134993390ece0edf847aa03476b && \
    git checkout FETCH_HEAD

WORKDIR /workspace/uv

# Pre-fetch and pre-build dependencies for the uv-pep508 crate (the only crate
# the tests touch). Failures here are tolerated so the image still builds when
# upstream lockfiles drift; the test step will surface real compile errors.
RUN cargo fetch
RUN cargo build -p uv-pep508 --tests || true
RUN cargo build -p uv-pep508 --tests --features non-pep508-extensions || true

RUN mkdir -p /logs/verifier
