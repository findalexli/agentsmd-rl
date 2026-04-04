FROM rust:1.88-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/zeroclaw && \
    cd /workspace/zeroclaw && \
    git remote add origin https://github.com/zeroclaw-labs/zeroclaw.git && \
    git fetch --depth=1 origin 3e02e68ec0e26b2c43593c40d660e2298c8cb332 && \
    git checkout FETCH_HEAD



RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/zeroclaw