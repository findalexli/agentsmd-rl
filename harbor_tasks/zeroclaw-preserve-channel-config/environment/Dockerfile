FROM rust:1.88-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    pkg-config protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/zeroclaw && \
    cd /workspace/zeroclaw && \
    git remote add origin https://github.com/zeroclaw-labs/zeroclaw.git && \
    git fetch --depth=1 origin ce6dd7ca3740473e6414c3eee3d8172e15d79758 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/zeroclaw

# Fix duplicate flate2+tar keys in Cargo.toml at this commit
RUN sed -i '98,99d' Cargo.toml

# Pre-fetch deps and pre-compile for fast incremental cargo check during tests
RUN cargo fetch
RUN cargo check || true

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"