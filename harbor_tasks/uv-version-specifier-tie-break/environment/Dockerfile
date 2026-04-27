FROM rust:1.95-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=never \
    CARGO_INCREMENTAL=0

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        python3 \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 \
        pytest-json-ctrf==0.4.1

WORKDIR /workspace

RUN git init /workspace/uv && \
    cd /workspace/uv && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 796ceb2790a394ab1d238b8d57965a99e5e10a05 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/uv

RUN cargo fetch --locked

RUN cargo build -p uv-pep440 --tests --quiet 2>&1 | tail -3 || true

RUN mkdir -p /logs/verifier
