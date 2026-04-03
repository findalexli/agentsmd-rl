FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages pytest pytest-json-ctrf

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/zeroclaw && \
    cd /workspace/zeroclaw && \
    git remote add origin https://github.com/zeroclaw-labs/zeroclaw.git && \
    git fetch --depth=1 origin 753d4fc65f32b45797e7aba52db6c8eb3a24ad89 && \
    git checkout FETCH_HEAD

# Pre-compile dependencies so test runs are faster
RUN cd /workspace/zeroclaw && cargo fetch
RUN cd /workspace/zeroclaw && cargo check --all-targets 2>&1 || true

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/zeroclaw